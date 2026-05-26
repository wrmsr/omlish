import asyncio
import traceback
import typing as ta
import uuid
import weakref

from omdev import clipboard as cpb
from omdev.tui import textual as tx
from omlish import check
from omlish import dataclasses as dc
from omlish.asyncs.relays import SchedulingAsyncBufferRelay
from omlish.logs import all as logs

from ...... import minichain as mc
from ..termrender import BackgroundTerminalRenderer
from ..widgets.messages.ai import StaticAiMessage
from ..widgets.messages.ai import StreamAiMessage
from ..widgets.messages.base import Message
from ..widgets.messages.base import MessageFinalized
from ..widgets.messages.container import MessagesContainer
from ..widgets.messages.stream import ContentStreamMessagePart
from ..widgets.messages.stream import FinalStreamMessagePart
from ..widgets.messages.stream import StreamMessagePart
from ..widgets.messages.tools import ToolConfirmationMessage
from ..widgets.messages.tools import ToolMessage
from ..widgets.messages.ui import UiMessage
from ..widgets.messages.user import UserMessage
from ..widgets.messages.welcome import WelcomeMessage
from .types import ChatDriverInterfaceState
from .types import ChatDriverInterfaceStateListener


log, alog = logs.get_module_loggers(globals())


##


ChatEventQueue = ta.NewType('ChatEventQueue', asyncio.Queue)


class ChatDriverInterface(
    tx.ComposeOnce,
    tx.InitAddClass,
    tx.Widget,
):
    init_add_class = 'chat-driver-interface'

    def __init__(
            self,
            *,
            chat_facade: mc.facades.Facade,
            chat_driver: mc.drivers.Driver,
            commands_manager: mc.facades.CommandsManager,
            chat_event_queue: ChatEventQueue,
            background_terminal_renderer: BackgroundTerminalRenderer,
            clipboard: cpb.Clipboard | None = None,
            state_listener: ChatDriverInterfaceStateListener | None = None,
            welcome_message: WelcomeMessage | None = None,
            chat_id: mc.drivers.ChatId,
    ) -> None:
        super().__init__()

        self._chat_facade = chat_facade
        self._chat_driver = chat_driver
        self._commands_manager = commands_manager
        self._chat_event_queue = chat_event_queue
        self._background_terminal_renderer = background_terminal_renderer
        self._clipboard = clipboard
        self._state_listener = state_listener
        self._chat_id = chat_id

        #

        self._chat_action_queue: asyncio.Queue[ta.Any] = asyncio.Queue()

        self._pending_tool_confirmations: set[ToolConfirmationMessage] = set()

        self._append_stream_message_buffer: SchedulingAsyncBufferRelay[StreamMessagePart] = SchedulingAsyncBufferRelay(  # noqa
            self._schedule_drain_append_stream_message_buffer,
        )

        self._suppressed_background_terminal_render_set: ta.MutableSet[tx.Widget] = weakref.WeakSet()

        #

        self._messages_container = MessagesContainer(
            [welcome_message] if welcome_message is not None else [],
            clipboard=self._clipboard,
            chat_uuid=chat_id.v,
        )

    #

    _state: ChatDriverInterfaceState = ChatDriverInterfaceState.IDLE

    async def _set_state(self, st: ChatDriverInterfaceState) -> None:
        if self._state == st:
            return

        self._state = st

        if (sl := self._state_listener) is not None:
            await sl(self, st)

    @property
    def state(self) -> ChatDriverInterfaceState:
        return self._state

    ##
    # Compose

    def _compose_once(self) -> tx.ComposeResult:
        yield self._messages_container

    ##
    # Mounting

    async def on_mount(self) -> None:
        check.state(self._chat_event_queue_task is None)
        self._chat_event_queue_task = asyncio.create_task(self._chat_event_queue_task_main())

        check.state(self._chat_action_queue_task is None)
        self._chat_action_queue_task = asyncio.create_task(self._chat_action_queue_task_main())

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
    # Messages

    @tx.on(MessageFinalized)
    async def _on_message_finalized(self, event: MessageFinalized) -> None:
        if event.widget in self._suppressed_background_terminal_render_set:
            self._suppressed_background_terminal_render_set.remove(event.widget)
            return

        if isinstance(event.widget, WelcomeMessage):
            return

        async def inner() -> None:
            await self._background_terminal_renderer.background_render_widget(event.widget)

        self.refresh(layout=True)
        self.call_after_refresh(inner)

    async def _schedule_drain_append_stream_message_buffer(self) -> None:
        self.call_next(self._drain_append_stream_message_buffer)

    async def _drain_append_stream_message_buffer(self) -> None:
        parts = await self._append_stream_message_buffer.swap()
        await self._messages_container.append_stream_message_content(parts)

    async def mount_messages(
            self,
            chat: mc.Chat,
            *,
            suppress_background_terminal_render: bool = False,
    ) -> None:
        wx: list[Message] = []

        for msg in chat:
            if isinstance(msg, mc.AiMessage):
                wx.append(
                    StaticAiMessage(
                        check.isinstance(msg.c, str),
                        markdown=True,
                        message_uuid=msg.metadata[mc.MessageUuid].v,
                    ),
                )

            elif isinstance(msg, mc.UserMessage):
                wx.append(UserMessage(
                    check.isinstance(msg.c, str),
                    message_uuid=msg.metadata[mc.MessageUuid].v,
                ))

        if not wx:
            return

        if suppress_background_terminal_render:
            for w in wx:
                self._suppressed_background_terminal_render_set.add(w)

        await self._messages_container.enqueue_mount_messages(*wx)
        self.call_later(self._messages_container.mount_messages)

    ##
    # Chat events

    _chat_event_queue_task: asyncio.Task[None] | None = None

    async def _handle_chat_queue_event(self, ev: ta.Any) -> None:
        if isinstance(ev, mc.AiMessagesEvent):
            if not ev.streamed:
                ai_msgs = [
                    msg
                    for msg in ev.chat
                    if isinstance(msg, mc.AiMessage)
                ]

                if ai_msgs:
                    await self.mount_messages(ai_msgs)

        elif isinstance(ev, mc.AiStreamBeginEvent):
            # self.call_later(self._messages_container.mount_messages, StreamAiMessage(message_uuid=ev.message_uuid))  # noqa
            pass

        elif isinstance(ev, mc.AiStreamDeltaEvent):
            if isinstance(ev.delta, mc.ContentAiDelta):
                await self._append_stream_message_buffer.push(
                    ContentStreamMessagePart(
                        StreamAiMessage,
                        check.not_none(ev.message_uuid),
                        check.isinstance(ev.delta.c, str),
                    ),
                )

            elif isinstance(ev.delta, mc.ToolUseAiDelta):
                pass

        elif isinstance(ev, mc.AiStreamEndEvent):
            await self._append_stream_message_buffer.push(
                FinalStreamMessagePart(
                    StreamAiMessage,
                    check.not_none(ev.message_uuid),
                ),
            )

        elif isinstance(ev, mc.ToolUseEvent):
            tr_dct = dict(
                id=ev.tue.use.id,
                name=check.not_none(ev.tue.catalog_entry).spec.name,
                args=ev.tue.use.args,
                # spec=msh.marshal(tce.spec),
            )

            tr_uit = mc.render_obj_json_ui_text(
                tr_dct,
                mc.JsonUiTextRendering(
                    'pretty',
                    five=True,
                    multiline_strings=True,
                ),
            )

            tr_rt = mc.ui_text_to_rich_text(tr_uit)

            tm = ToolMessage(
                tx.Text(ev.tue.use.name),
                tr_rt,
                ToolMessage.State.RUNNING,
            )

            self._suppressed_background_terminal_render_set.add(tm)
            await self._messages_container.enqueue_mount_messages(tm)
            self.call_later(self._messages_container.mount_messages)

        elif isinstance(ev, mc.ToolUseResultEvent):
            pass

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

    async def _show_exception(self, e: BaseException) -> None:
        e_msg = '\n\n'.join([
            *(
                [''.join(traceback.format_exception(type(e), e, e.__traceback__)).strip()]
                if e.__traceback__ is not None else []
            ),
            repr(e).strip(),
            *([e_str] if (e_str := str(e)).strip() else []),
        ])

        await self.display_ui_message(tx.Text(e_msg))

    @dc.dataclass(frozen=True)
    class UserInput:
        text: str

        _: dc.KW_ONLY

        input_uuid: uuid.UUID | None = None

    async def execute_user_input(self, ac: UserInput) -> None:
        try:
            await self._chat_facade.handle_user_input(
                ac.text,
                input_uuid=ac.input_uuid,
            )

        except Exception as e:  # noqa
            await self._show_exception(e)

    #

    _cur_chat_action: asyncio.Task[None] | None = None

    async def _execute_chat_action(self, fn: ta.Callable[[], ta.Any]) -> None:
        check.state(self._cur_chat_action is None)
        check.state(self._state == ChatDriverInterfaceState.IDLE)

        self._cur_chat_action = cca = asyncio.create_task(fn())

        try:
            await self._set_state(ChatDriverInterfaceState.ACTIVE)

            await cca

        except asyncio.CancelledError:
            async def show_cancelled() -> None:
                await self.display_ui_message(tx.Text('Chat action cancelled'))

            self.call_next(show_cancelled)

        except BaseException as e:  # noqa
            self.call_next(self._show_exception, e)

            raise

        finally:
            self._cur_chat_action = None

            async def set_idle() -> None:
                await self._set_state(ChatDriverInterfaceState.IDLE)

            self.call_next(set_idle)

    #

    _chat_action_queue_task: asyncio.Task[None] | None = None

    @logs.async_exception_logging(alog, BaseException)
    async def _chat_action_queue_task_main(self) -> None:
        while True:
            ac = await self._chat_action_queue.get()
            if ac is None:
                break

            await alog.debug(lambda: f'Got chat action: {ac!r}')

            if isinstance(ac, ChatDriverInterface.UserInput):
                await self._execute_chat_action(lambda: self.execute_user_input(ac))

            else:
                raise TypeError(ac)  # noqa

    ##
    # Input

    async def send_user_input(self, s: str, *, no_echo: bool = False) -> None:
        input_uuid = uuid.uuid7()

        if not no_echo:
            await self._messages_container.mount_messages(
                UserMessage(
                    tx.Text(s),
                    message_uuid=input_uuid,
                ),
            )

        await self._chat_action_queue.put(
            ChatDriverInterface.UserInput(
                s,
                input_uuid=input_uuid,
            ),
        )

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

    async def cancel_current_action(self) -> None:
        if (cat := self._cur_chat_action) is not None:
            cat.cancel()

    async def respond_to_all_pending_tool_uses(self, allowed: bool) -> None:
        for tcm in list(self._pending_tool_confirmations):
            if not tcm.has_rendered:
                continue

            if not tcm.has_responded:
                await tcm.respond(allowed)

            self._pending_tool_confirmations.discard(tcm)

    ##
    # Commands

    def get_commands(self) -> ta.Sequence[mc.facades.Command]:
        return list(self._commands_manager.get_commands().values())

    async def handle_quit(self) -> None:
        self.app.exit()
