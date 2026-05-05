import typing as ta
import weakref

from omdev.tui import textual as tx
from omlish.logs import all as logs

from .drivers.interface import ChatDriverInterface
from .drivers.types import ChatDriverInterfaceState
from .inputhistory import InputHistoryManager
from .styles import read_app_css
from .suggestions import SuggestionsManager
from .widgets.input import InputContainer
from .widgets.input import InputTextArea
from .widgets.status import StatusContainer


log, alog = logs.get_module_loggers(globals())


##


class ChatAppScreen(tx.Screen):
    BINDINGS: ta.ClassVar[ta.Sequence[tx.BindingType]] = [
        tx.Binding(
            'alt+c,super+c',
            'screen.copy_text',
            'Copy selected text',
            show=False,
        ),

        tx.Binding(
            'f10',
            'app.allow_all_pending_tool_uses',
            'Allows all pending tool uses',
        ),

        tx.Binding(
            'f2',
            'app.deny_all_pending_tool_uses',
            'Denies all pending tool uses',
        ),
    ]

    @classmethod
    def _merge_bindings(cls) -> tx.BindingsMap:
        return tx.unbind_map_keys(super()._merge_bindings(), ['ctrl+c'])


class ChatApp(
    tx.ComposeOnce,
    tx.ClipboardAppMixin,
    tx.DevtoolsAppMixin,
    tx.App,
):
    ENABLE_COMMAND_PALETTE: ta.ClassVar[bool] = False

    BINDINGS: ta.ClassVar[ta.Sequence[tx.BindingType]] = [
        *tx.App.BINDINGS,

        tx.Binding(
            'ctrl+z',  # FIXME: remap undo
            'suspend_process',
            'Suspend',
            show=False,
            priority=True,
        ),

        tx.Binding(
            'alt+z',
            'global_undo',
            'Undo',
            show=False,
            priority=True,
        ),

        tx.Binding(
            'alt+z',
            'global_redo',
            'Undo',
            show=False,
            priority=True,
        ),

        tx.Binding(
            'escape',
            'cancel',
            'Cancel current operation',
            show=False,
            priority=True,
        ),
    ]

    AUTO_FOCUS = '.input-container'

    def __init__(
            self,
            *,
            devtools_setup: tx.DevtoolsSetup | None = None,
            input_history_manager: InputHistoryManager,
            suggestions_manager: SuggestionsManager,

            chat_driver_interface: ChatDriverInterface,
    ) -> None:
        super().__init__()

        if devtools_setup is not None:
            devtools_setup(self)

        self._input_history_manager = input_history_manager

        self._chat_driver_interface = chat_driver_interface

        #

        self._input_focused_key_events: weakref.WeakSet[tx.Key] = weakref.WeakSet()

        #

        self._input_container = InputContainer(
            input_history_manager=input_history_manager,
            suggestions_manager=suggestions_manager,
        )

        self._status_container = StatusContainer()

    def get_driver_class(self) -> type[tx.Driver]:
        return tx.get_pending_writes_driver_class(super().get_driver_class())

    def get_default_screen(self) -> tx.Screen:
        return ChatAppScreen(id='_default')

    CSS: ta.ClassVar[str] = read_app_css()

    ##
    # Compose

    def _compose_once(self) -> tx.ComposeResult:
        yield self._chat_driver_interface
        yield self._input_container
        yield self._status_container

    ##
    # Mounting

    async def on_mount(self) -> None:
        self._input_container.input_text_area.focus()

        self.app_resume_signal.subscribe(self, self._after_resume)

    def _after_resume(self, _: ta.Any) -> None:
        self.call_later(self._hard_redraw)

    def _hard_redraw(self) -> None:
        self.refresh(repaint=True, layout=True)
        self.screen.refresh(repaint=True, layout=True)

    ##
    # Input

    @tx.on(InputTextArea.Submitted)
    async def on_input_text_area_submitted(self, event: InputTextArea.Submitted) -> None:
        self._input_container.input_text_area.clear()

        await self._input_history_manager.add(event.text)

        await self._chat_driver_interface.send_user_input(event.text)

    @tx.on(tx.Key)
    async def on_key(self, event: tx.Key) -> None:
        if event in self._input_focused_key_events:
            return

        if not (ita := self._input_container.input_text_area).has_focus:
            self._input_focused_key_events.add(event)

            ita.focus()

            self.screen.post_message(tx.Key(event.key, event.character))

    async def action_global_undo(self) -> None:
        if (focused := self.focused) is not None and hasattr(focused, 'action_undo'):
            focused.action_undo()

    async def action_global_redo(self) -> None:
        if (focused := self.focused) is not None and hasattr(focused, 'action_redo'):
            focused.action_redo()

    async def action_cancel(self) -> None:
        await self._chat_driver_interface.cancel_current_action()

    async def action_allow_all_pending_tool_uses(self) -> None:
        await self._chat_driver_interface.respond_to_all_pending_tool_uses(True)

    async def action_deny_all_pending_tool_uses(self) -> None:
        await self._chat_driver_interface.respond_to_all_pending_tool_uses(False)

    ##
    # Status bar

    async def _on_driver_state_change(self, driver: ChatDriverInterface, state: ChatDriverInterfaceState) -> None:
        # FIXME: multiple drivers
        self._status_container.set_driver_state(state)
