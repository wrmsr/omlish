import asyncio
import os
import typing as ta
import weakref

from omdev.tui import textual as tx
from omlish import check
from omlish import dataclasses as dc
from omlish import lang
from omlish.logs import all as logs
from omlish.term.alt import render_write_from_alt

from ...... import minichain as mc
from .....backends.types import BackendName
from ....types import SessionProfileName
from ...drivers.events.types import AiDeltaChatEvent
from ...drivers.events.types import AiMessagesChatEvent
from ...drivers.events.types import UserMessagesChatEvent
from ...drivers.types import ChatDriver
from ...facades.facade import ChatFacade
from .inputhistory import InputHistoryManager
from .styles import read_app_css
from .suggestions import SuggestionsManager
from .widgets.input import InputContainer
from .widgets.input import InputTextArea
from .widgets.messages import AiMessage
from .widgets.messages import MessageDivider
from .widgets.messages import MessagesContainer
from .widgets.messages import StaticAiMessage
from .widgets.messages import StreamAiMessage
from .widgets.messages import ToolConfirmationMessage
from .widgets.messages import UiMessage
from .widgets.messages import UserMessage
from .widgets.messages import WelcomeMessage
from .widgets.status import StatusContainer


log, alog = logs.get_module_loggers(globals())


##


ChatEventQueue = ta.NewType('ChatEventQueue', asyncio.Queue)


##


class ChatAppGetter(lang.AsyncCachedFunc0['ChatApp']):
    pass


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
            'f11',
            'app.deny_all_pending_tool_uses',
            'Denies all pending tool uses',
        ),
    ]

    @classmethod
    def _merge_bindings(cls) -> tx.BindingsMap:
        return tx.unbind_map_keys(super()._merge_bindings(), ['ctrl+c'])


class ChatApp(
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
            chat_driver: ChatDriver,
            chat_event_queue: ChatEventQueue,
            backend_name: BackendName | None = None,
            devtools_setup: tx.DevtoolsSetup | None = None,
            input_history_manager: InputHistoryManager,
            session_profile_name: SessionProfileName | None = None,
            suggestions_manager: SuggestionsManager,
    ) -> None:
        super().__init__()

        if devtools_setup is not None:
            devtools_setup(self)

        self._chat_facade = chat_facade
        self._chat_driver = chat_driver
        self._chat_event_queue = chat_event_queue
        self._backend_name = backend_name
        self._input_history_manager = input_history_manager
        self._session_profile_name = session_profile_name
        self._suggestions_manager = suggestions_manager

        #

        self._chat_action_queue: asyncio.Queue[ta.Any] = asyncio.Queue()

        self._input_focused_key_events: weakref.WeakSet[tx.Key] = weakref.WeakSet()

        self._pending_tool_confirmations: set[ToolConfirmationMessage] = set()

        #

        self._messages_container = MessagesContainer()

        self._input_container = InputContainer(
            suggestions_manager=self._suggestions_manager,
        )

        self._status_container = StatusContainer()

    def get_driver_class(self) -> type[tx.Driver]:
        return tx.get_pending_writes_driver_class(super().get_driver_class())

    def get_default_screen(self) -> tx.Screen:
        return ChatAppScreen(id='_default')

    CSS: ta.ClassVar[str] = read_app_css()

    ##
    # Compose

    _has_composed = False

    def compose(self) -> tx.ComposeResult:
        check.state(not self._has_composed)
        self._has_composed = True

        #

        yield self._messages_container
        yield self._input_container
        yield self._status_container

    ##
    # Widget getters

    def _get_input_text_area(self) -> InputTextArea:
        return self.query_one('#input', InputTextArea)

    def _get_messages_container(self) -> tx.VerticalScroll:
        return self.query_one('#messages-container', MessagesContainer)

    ##
    # Messages

    def _is_messages_at_bottom(self, threshold: int = 3) -> bool:
        return (ms := self._get_messages_container()).scroll_y >= (ms.max_scroll_y - threshold)

    def _scroll_messages_to_bottom(self) -> None:
        self._get_messages_container().scroll_end(animate=False)

    def _anchor_messages(self) -> None:
        if (ms := self._get_messages_container()).max_scroll_y:
            ms.anchor()

    def _scroll_messages_to_bottom_and_anchor(self) -> None:
        self._scroll_messages_to_bottom()
        self._anchor_messages()

    #

    _pending_mount_messages: list[tx.Widget] | None = None

    async def _enqueue_mount_messages(self, *messages: tx.Widget) -> None:
        if (lst := self._pending_mount_messages) is None:
            lst = self._pending_mount_messages = []

        lst.extend(messages)

    _stream_ai_message: StreamAiMessage | None = None

    async def _finalize_stream_ai_message(self) -> None:
        if (aim := self._stream_ai_message) is None:
            return

        await aim.stop_stream()
        self._stream_ai_message = None

    async def _append_stream_ai_message_content(self, content: str) -> None:
        if (sam := self._stream_ai_message) is not None:
            was_at_bottom = self._is_messages_at_bottom()

            await sam.append_content(content)

            if was_at_bottom:
                self.call_after_refresh(self._scroll_messages_to_bottom_and_anchor)

        else:
            await self._mount_messages(StreamAiMessage(content))

    _num_mounted_messages = 0

    async def _mount_messages(self, *messages: tx.Widget) -> None:
        was_at_bottom = self._is_messages_at_bottom()

        msg_ctr = self._get_messages_container()

        for msg in [*(self._pending_mount_messages or []), *messages]:
            if isinstance(msg, (AiMessage, ToolConfirmationMessage)):
                await self._finalize_stream_ai_message()

            if self._num_mounted_messages:
                await msg_ctr.mount(MessageDivider(lang.localnow().strftime('%Y-%m-%d %H:%M:%S')))

            await msg_ctr.mount(msg)

            self._num_mounted_messages += 1

            if isinstance(msg, StreamAiMessage):
                self._stream_ai_message = check.replacing_none(self._stream_ai_message, msg)
                await msg.write_initial_content()

        self._pending_mount_messages = None

        self.call_after_refresh(self._scroll_messages_to_bottom)

        if was_at_bottom:
            self.call_after_refresh(self._anchor_messages)

    #

    # class RenderSandbox(tx.Container):
    #     def __init__(self, **kwargs: ta.Any) -> None:
    #         super().__init__(**kwargs)
    #
    #         self.display = 'none'

    # async def _render_widget_ansi(self, widget, width=80):
    #     # Mount temporarily
    #     await self._render_sandbox.mount(widget)
    #
    #     # Force layout so virtual_size gets computed
    #     self.refresh(layout=True)
    #
    #     # Give Textual a tick to process layout
    #     await self.run_action('refresh')
    #
    #     widget.styles.width = width
    #
    #     height = 10  # widget.virtual_size.height or widget.size.height
    #
    #     console = tx.Console(
    #         width=width,
    #         height=height,
    #         record=True,
    #         force_terminal=True,
    #         color_system=ta.cast(ta.Any, self.console.color_system or 'auto'),
    #     )
    #
    #     for line in widget.render_lines(tx.Region(0, 0, width, height)):
    #         console.print(line)
    #
    #     ansi = console.export_text(styles=True)
    #
    #     await widget.remove()
    #
    #     return ansi

    async def _background_render_chat(self, chat: mc.Chat) -> None:
        lst: list[str] = []

        for msg in chat:  # noqa
            # if (c := MessageContentExtractorImpl().extract_message_content(msg)) is not None:
            #     if (s := ContentStringifierImpl().stringify_content(c)) is not None and (s := s.strip()):
            #         if len(lst):
            #             lst.append('\n\n')
            #         lst.append(await self._render_widget_ansi(tx.Markdown(s)))
            # FIXME: GARBAGE ALL GARBAGE
            pass

        if not lst:
            return

        pwd = check.isinstance(self._driver, tx.PendingWritesDriverMixin)
        pwd.queue_primary_buffer_write(render_write_from_alt(*lst, '\n\n'))

        self.refresh()

    ##
    # Chat events

    _chat_event_queue_task: asyncio.Task[None] | None = None

    @logs.async_exception_logging(alog, BaseException)
    async def _chat_event_queue_task_main(self) -> None:
        while True:
            ev = await self._chat_event_queue.get()
            if ev is None:
                break

            await alog.debug(lambda: f'Got chat event: {ev!r}')

            if isinstance(ev, AiMessagesChatEvent):
                if ev.streamed:
                    await self._finalize_stream_ai_message()
                    await self._background_render_chat(ev.chat)

                else:
                    wx: list[tx.Widget] = []

                    for ai_msg in ev.chat:
                        if isinstance(ai_msg, mc.AiMessage):
                            wx.append(
                                StaticAiMessage(
                                    check.isinstance(ai_msg.c, str),
                                    markdown=True,
                                ),
                            )

                    if wx:
                        await self._enqueue_mount_messages(*wx)
                        self.call_later(self._mount_messages)

            elif isinstance(ev, AiDeltaChatEvent):
                if isinstance(ev.delta, mc.ContentAiDelta):
                    cc = check.isinstance(ev.delta.c, str)
                    self.call_later(self._append_stream_ai_message_content, cc)

                elif isinstance(ev.delta, mc.ToolUseAiDelta):
                    pass

            elif isinstance(ev, UserMessagesChatEvent):
                await self._background_render_chat(ev.chat)

    ##
    # Chat actions

    @dc.dataclass(frozen=True)
    class UserInput:
        text: str

    async def _execute_user_input(self, ac: UserInput) -> None:
        try:
            await self._chat_facade.handle_user_input(ac.text)
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

        await self._chat_driver.start()

        check.state(self._chat_action_queue_task is None)
        self._chat_action_queue_task = asyncio.create_task(self._chat_action_queue_task_main())

        self._get_input_text_area().focus()

        await self._mount_messages(
            WelcomeMessage('\n'.join([
                *([f'Profile: {self._session_profile_name}'] if self._session_profile_name is not None else []),
                f'Backend: {self._backend_name or "?"}',
                f'Dir: {os.getcwd()}',
            ])),
        )

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

    @tx.on(InputTextArea.Submitted)
    async def on_input_text_area_submitted(self, event: InputTextArea.Submitted) -> None:
        self._get_input_text_area().clear()

        await self._finalize_stream_ai_message()

        await self._mount_messages(UserMessage(event.text))

        await self._input_history_manager.add(event.text)

        await self._chat_action_queue.put(ChatApp.UserInput(event.text))

    def _move_input_cursor_to_end(self) -> None:
        ita = self._get_input_text_area()
        ln = ita.document.line_count - 1
        lt = ita.document.lines[ln]
        ita.move_cursor((ln, len(lt)))

    @tx.on(InputTextArea.HistoryPrevious)
    async def on_input_text_area_history_previous(self, event: InputTextArea.HistoryPrevious) -> None:
        await self._input_history_manager.load_if_necessary()
        if (entry := self._input_history_manager.get_previous(event.text)) is not None:
            self._get_input_text_area().text = entry
            self._move_input_cursor_to_end()

    @tx.on(InputTextArea.HistoryNext)
    async def on_input_text_area_history_next(self, event: InputTextArea.HistoryNext) -> None:
        await self._input_history_manager.load_if_necessary()
        if (entry := self._input_history_manager.get_next(event.text)) is not None:
            ita = self._get_input_text_area()
            ita.text = entry
            self._move_input_cursor_to_end()
        else:
            # At the end of history, clear the input
            ita = self._get_input_text_area()
            ita.clear()
            self._input_history_manager.reset_position()

    @tx.on(tx.Key)
    async def on_key(self, event: tx.Key) -> None:
        if event in self._input_focused_key_events:
            return

        chat_input = self._get_input_text_area()

        if not chat_input.has_focus:
            self._input_focused_key_events.add(event)

            chat_input.focus()

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
            await self._mount_messages(tcm)

        self.call_later(inner)

        ret = await fut

        return ret

    async def display_ui_message(
            self,
            content: tx.VisualType,
    ) -> None:
        await self._mount_messages(UiMessage(content))

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
