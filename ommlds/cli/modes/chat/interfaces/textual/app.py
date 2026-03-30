import asyncio
import typing as ta
import uuid
import weakref

from omdev.tui import textual as tx
from omlish import check
from omlish import dataclasses as dc
from omlish.logs import all as logs

from ...... import minichain as mc
from ...facades.facade import ChatFacade
from .inputhistory import InputHistoryManager
from .styles import read_app_css
from .suggestions import SuggestionsManager
from .termrender import BackgroundTerminalRenderer
from .widgets.input import InputContainer
from .widgets.input import InputTextArea
from .widgets.messages import Message
from .widgets.messages import MessageFinalized
from .widgets.messages import MessagesContainer
from .widgets.messages import StaticAiMessage
from .widgets.messages import ToolConfirmationMessage
from .widgets.messages import UiMessage
from .widgets.messages import UserMessage
from .widgets.messages import WelcomeMessage
from .widgets.status import StatusContainer


log, alog = logs.get_module_loggers(globals())


##


ChatEventQueue = ta.NewType('ChatEventQueue', asyncio.Queue)


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
            'escape',
            'cancel',
            'Cancel current operation',
            show=False,
            priority=True,
        ),
    ]

    def __init__(
            self,
            *,
            chat_facade: ChatFacade,
            chat_driver: mc.drivers.Driver,
            chat_event_queue: ChatEventQueue,
            devtools_setup: tx.DevtoolsSetup | None = None,
            input_history_manager: InputHistoryManager,
            suggestions_manager: SuggestionsManager,
            background_terminal_renderer: BackgroundTerminalRenderer,
            welcome_message: WelcomeMessage | None = None,
    ) -> None:
        super().__init__()

        if devtools_setup is not None:
            devtools_setup(self)

        self._chat_facade = chat_facade
        self._chat_driver = chat_driver
        self._chat_event_queue = chat_event_queue
        self._input_history_manager = input_history_manager
        self._background_terminal_renderer = background_terminal_renderer

        #

        self._chat_action_queue: asyncio.Queue[ta.Any] = asyncio.Queue()

        self._input_focused_key_events: weakref.WeakSet[tx.Key] = weakref.WeakSet()

        self._pending_tool_confirmations: set[ToolConfirmationMessage] = set()

        #

        self._messages_container = MessagesContainer([welcome_message] if welcome_message is not None else [])

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
        yield self._messages_container
        yield self._input_container
        yield self._status_container

    ##
    # Messages

    async def _on_message_finalized(self, event: MessageFinalized) -> None:
        if isinstance(event.widget, WelcomeMessage):
            return

        async def inner() -> None:
            await self._background_terminal_renderer.background_render_widget(event.widget)

        self.refresh(layout=True)
        self.call_after_refresh(inner)

    ##
    # Chat events

    _chat_event_queue_task: asyncio.Task[None] | None = None

    async def _handle_chat_queue_event(self, ev: ta.Any) -> None:
        if isinstance(ev, mc.drivers.AiMessagesEvent):
            if not ev.streamed:
                wx: list[Message] = []

                for ai_msg in ev.chat:
                    if isinstance(ai_msg, mc.AiMessage):
                        wx.append(
                            StaticAiMessage(
                                check.isinstance(ai_msg.c, str),
                                markdown=True,
                                message_uuid=ai_msg.metadata[mc.MessageUuid].v,
                            ),
                        )

                if wx:
                    await self._messages_container.enqueue_mount_messages(*wx)
                    self.call_later(self._messages_container.mount_messages)

        elif isinstance(ev, mc.drivers.AiStreamBeginEvent):
            # self.call_later(self._messages_container.mount_messages, StreamAiMessage(message_uuid=ev.message_uuid))  # noqa
            pass

        elif isinstance(ev, mc.drivers.AiStreamDeltaEvent):
            if isinstance(ev.delta, mc.ContentAiDelta):
                cc = check.isinstance(ev.delta.c, str)
                # FIXME: append to internal buffer
                self.call_later(self._messages_container.append_stream_ai_message_content, ev.message_uuid, cc)  # noqa

            elif isinstance(ev.delta, mc.ToolUseAiDelta):
                pass

        elif isinstance(ev, mc.drivers.AiStreamEndEvent):
            self.call_later(self._messages_container.finalize_stream_ai_message, ev.message_uuid)

    @logs.async_exception_logging(alog, BaseException)
    async def _chat_event_queue_task_main(self) -> None:
        while True:
            ev = await self._chat_event_queue.get()
            if ev is None:
                break

            await alog.debug(lambda: f'Got chat event: {ev!r}')

            await self._handle_chat_queue_event(ev)

    ##
    # Chat actions

    @dc.dataclass(frozen=True)
    class UserInput:
        text: str

        _: dc.KW_ONLY

        input_uuid: uuid.UUID | None = None

    async def _execute_user_input(self, ac: UserInput) -> None:
        try:
            await self._chat_facade.handle_user_input(
                ac.text,
                input_uuid=ac.input_uuid,
            )

        except Exception as e:  # noqa
            # raise
            await self.display_ui_message(tx.Text(repr(e)))

    #

    _cur_chat_action: asyncio.Task[None] | None = None

    async def _execute_chat_action(self, fn: ta.Callable[[], ta.Any]) -> None:
        check.state(self._cur_chat_action is None)

        self._cur_chat_action = asyncio.create_task(fn())

        try:
            await self._cur_chat_action

        except asyncio.CancelledError:
            pass

        except BaseException as e:  # noqa
            raise

        finally:
            self._cur_chat_action = None

    #

    _chat_action_queue_task: asyncio.Task[None] | None = None

    @logs.async_exception_logging(alog, BaseException)
    async def _chat_action_queue_task_main(self) -> None:
        while True:
            ac = await self._chat_action_queue.get()
            if ac is None:
                break

            await alog.debug(lambda: f'Got chat action: {ac!r}')

            if isinstance(ac, ChatApp.UserInput):
                await self._execute_chat_action(lambda: self._execute_user_input(ac))

            else:
                raise TypeError(ac)  # noqa

    ##
    # Mounting

    async def on_mount(self) -> None:
        check.state(self._chat_event_queue_task is None)
        self._chat_event_queue_task = asyncio.create_task(self._chat_event_queue_task_main())

        check.state(self._chat_action_queue_task is None)
        self._chat_action_queue_task = asyncio.create_task(self._chat_action_queue_task_main())

        self._input_container.input_text_area.focus()

        await self._messages_container.mount_messages()

        self.call_after_refresh(self._chat_driver.start)

    async def on_unmount(self) -> None:
        if (cat := self._chat_action_queue_task) is not None:
            await self._chat_action_queue.put(None)
            await cat

        await self._chat_driver.stop()

        if (cet := self._chat_event_queue_task) is not None:
            await self._chat_event_queue.put(None)
            await cet

    ##
    # Input

    async def send_user_input(self, s: str, *, no_echo: bool = False) -> None:
        input_uuid = uuid.uuid4()

        if not no_echo:
            await self._messages_container.mount_messages(
                UserMessage(
                    s,
                    message_uuid=input_uuid,
                ),
            )

            await self._input_history_manager.add(s)

        await self._chat_action_queue.put(
            ChatApp.UserInput(
                s,
                input_uuid=input_uuid,
            ),
        )

    @tx.on(InputTextArea.Submitted)
    async def on_input_text_area_submitted(self, event: InputTextArea.Submitted) -> None:
        self._input_container.input_text_area.clear()

        await self._input_history_manager.add(event.text)

        await self.send_user_input(event.text)

    @tx.on(tx.Key)
    async def on_key(self, event: tx.Key) -> None:
        if event in self._input_focused_key_events:
            return

        if not (ita := self._input_container.input_text_area).has_focus:
            self._input_focused_key_events.add(event)

            ita.focus()

            self.screen.post_message(tx.Key(event.key, event.character))

    ##
    # User interaction

    async def confirm_tool_use(
            self,
            outer_message: tx.VisualType,
            inner_message: tx.VisualType,
    ) -> bool:
        fut: asyncio.Future[bool] = asyncio.get_running_loop().create_future()

        tcm = ToolConfirmationMessage(
            outer_message,
            inner_message,
            fut,
        )

        fut.add_done_callback(lambda _: self._pending_tool_confirmations.discard(tcm))

        self._pending_tool_confirmations.add(tcm)

        async def inner() -> None:
            await self._messages_container.mount_messages(tcm)

        self.call_later(inner)

        ret = await fut

        return ret

    async def display_ui_message(
            self,
            content: tx.VisualType,
    ) -> None:
        await self._messages_container.mount_messages(UiMessage(content))

    async def action_cancel(self) -> None:
        if (cat := self._cur_chat_action) is not None:
            cat.cancel()

    async def _respond_to_all_pending_tool_uses(self, allowed: bool) -> None:
        for tcm in list(self._pending_tool_confirmations):
            if not tcm.has_rendered:
                continue

            if not tcm.has_responded:
                await tcm.respond(allowed)

            self._pending_tool_confirmations.discard(tcm)

    async def action_allow_all_pending_tool_uses(self) -> None:
        await self._respond_to_all_pending_tool_uses(True)

    async def action_deny_all_pending_tool_uses(self) -> None:
        await self._respond_to_all_pending_tool_uses(False)
