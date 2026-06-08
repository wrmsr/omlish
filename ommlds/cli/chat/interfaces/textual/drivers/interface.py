import asyncio
import traceback
import typing as ta
import uuid
import weakref

from omdev import clipboard as cpb
from omdev.tui import textual as tx
from omlish import check
from omlish import dataclasses as dc
from omlish import lang
from omlish.asyncs.relays import SchedulingAsyncBufferRelay
from omlish.logs import all as logs

from ...... import minichain as mc
from ..termrender import BackgroundTerminalRenderer
from ..widgets.messages.base import Message
from ..widgets.messages.base import MessageFinalized
from ..widgets.messages.container import MessagesContainer
from ..widgets.messages.stream import ContentStreamMessagePart
from ..widgets.messages.stream import FinalStreamMessagePart
from ..widgets.messages.stream import StreamMessagePart
from ..widgets.messages.tools import ToolConfirmationMessage
from ..widgets.messages.tools import ToolMessage
from ..widgets.messages.ui import UiMessage
from ..widgets.messages.welcome import WelcomeMessage
from .timelines import build_item_message
from .timelines import build_tool_message
from .timelines import render_item_content_str
from .timelines import stream_message_cls_for_item
from .timelines import update_tool_message
from .types import ChatDriverInterfaceState
from .types import ChatDriverInterfaceStateListener
from .types import InitialTimelineWindowLimit


log, alog = logs.get_module_loggers(globals())


##


@dc.dataclass(frozen=True)
class _MountWidgetDisplayOp:
    widget: Message

    _: dc.KW_ONLY

    suppress_background_terminal_render: bool = False


@dc.dataclass(frozen=True)
class _MountWidgetsBeforeDisplayOp:
    widgets: ta.Sequence[Message]
    anchor: Message | None


@dc.dataclass(frozen=True)
class _UpdateToolDisplayOp:
    item: mc.facades.timelines.ToolUseTimelineItem


_DisplayOp: ta.TypeAlias = ta.Union[  # noqa
    _MountWidgetDisplayOp,
    _MountWidgetsBeforeDisplayOp,
    _UpdateToolDisplayOp,
    StreamMessagePart,
]


##


class ChatDriverInterface(
    tx.ComposeOnce,
    tx.InitAddClass,
    tx.Widget,
):
    """
    The per-driver chat surface: composes the messages container, consumes the driver's `Timeline` (initial window +
    live events) into widgets, and routes user input back to the facade. All display mutation funnels through one
    ordered, batched display-op relay; everything this widget renders comes from timeline items - it never interprets
    raw driver events.
    """

    init_add_class = 'chat-driver-interface'

    def __init__(
            self,
            *,
            chat_facade: mc.facades.Facade,
            chat_driver: mc.drivers.Driver,
            commands_manager: mc.facades.CommandsManager,
            timeline: mc.facades.timelines.Timeline,
            background_terminal_renderer: BackgroundTerminalRenderer,
            clipboard: cpb.Clipboard | None = None,
            state_listener: ChatDriverInterfaceStateListener | None = None,
            welcome_message: WelcomeMessage | None = None,
            chat_id: mc.drivers.ChatId,
            initial_timeline_window_limit: InitialTimelineWindowLimit = InitialTimelineWindowLimit(200),
            item_presenters: mc.facades.timelines.TimelineItemPresenters | None = None,
    ) -> None:
        super().__init__()

        self._chat_facade = chat_facade
        self._chat_driver = chat_driver
        self._commands_manager = commands_manager
        self._timeline = timeline
        self._background_terminal_renderer = background_terminal_renderer
        self._clipboard = clipboard
        self._state_listener = state_listener
        self._welcome_message = welcome_message
        self._chat_id = chat_id
        self._initial_timeline_window_limit = initial_timeline_window_limit
        self._item_presenters = item_presenters

        #

        self._chat_action_queue: asyncio.Queue[ta.Any] = asyncio.Queue()
        self._chat_driver_started: asyncio.Event = asyncio.Event()

        self._pending_tool_confirmations: set[ToolConfirmationMessage] = set()

        self._display_ops_pending: asyncio.Event = asyncio.Event()
        self._display_op_relay: SchedulingAsyncBufferRelay[_DisplayOp] = SchedulingAsyncBufferRelay(
            lang.as_async(self._display_ops_pending.set),
        )

        self._suppressed_background_terminal_render_set: ta.MutableSet[tx.Widget] = weakref.WeakSet()

        #

        self._timeline_items_by_id: dict[mc.facades.timelines.TimelineItemId, mc.facades.timelines.TimelineItem] = {}
        self._no_echo_input_uuids: set[uuid.UUID] = set()

        #

        self._messages_container = MessagesContainer(
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
        check.state(self._chat_action_queue_task is None)
        self._chat_action_queue_task = asyncio.create_task(self._chat_action_queue_task_main())

        check.state(self._display_ops_task is None)
        self._display_ops_task = asyncio.create_task(self._display_ops_task_main())

        check.state(self._timeline_task is None)
        self._timeline_task = asyncio.create_task(self._timeline_task_main())

        if (wm := self._welcome_message) is not None:
            await self._messages_container.mount_messages(wm)

        async def start_driver() -> None:
            # The timeline attaches only once the driver has fully started: startup phase callbacks perform storage
            # *writes* (e.g. last-chat-id), and overlapping them with the attach's storage reads trips sqlite's
            # no-retry deferred-transaction write-upgrade conflicts (SQLITE_BUSY_SNAPSHOT) in the current
            # session-per-connection orm setup.
            await self._chat_driver.start()
            self._chat_driver_started.set()

        self.call_after_refresh(start_driver)

    async def on_unmount(self) -> None:
        if (cat := self._chat_action_queue_task) is not None:
            await self._chat_action_queue.put(None)
            await cat

        await self._chat_driver.stop()

        if (tt := self._timeline_task) is not None:
            if (att := self._timeline_attachment) is not None:
                await att.subscription.aclose()
                await tt

            else:
                # Unmounted before the attach ever happened (the task may still be waiting on driver start).
                tt.cancel()
                try:
                    await tt
                except asyncio.CancelledError:
                    pass

        if (dot := self._display_ops_task) is not None:
            dot.cancel()
            try:
                await dot
            except asyncio.CancelledError:
                pass

    ##
    # Display ops - the single ordered funnel from timeline consumption to widget mutation.

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

    async def _apply_display_ops(self, ops: ta.Sequence[_DisplayOp]) -> None:
        stream_parts: list[StreamMessagePart] = []

        async def flush_stream_parts() -> None:
            if stream_parts:
                await self._messages_container.append_stream_message_content(stream_parts)
                stream_parts.clear()

        for op in ops:
            if isinstance(op, StreamMessagePart):
                stream_parts.append(op)
                continue

            await flush_stream_parts()

            if isinstance(op, _MountWidgetDisplayOp):
                if op.suppress_background_terminal_render:
                    self._suppressed_background_terminal_render_set.add(op.widget)

                await self._messages_container.mount_messages(op.widget)

            elif isinstance(op, _MountWidgetsBeforeDisplayOp):
                anchor = op.anchor
                if anchor is None or not anchor.is_mounted:
                    anchor = next(
                        (
                            ch for ch in self._messages_container.children
                            if isinstance(ch, Message) and not isinstance(ch, WelcomeMessage)
                        ),
                        None,
                    )

                for w in op.widgets:
                    self._suppressed_background_terminal_render_set.add(w)

                if anchor is not None and anchor.is_mounted:
                    await self._messages_container.mount_messages_before(anchor, *op.widgets)
                else:
                    await self._messages_container.mount_messages(*op.widgets)

            elif isinstance(op, _UpdateToolDisplayOp):
                tw = self._messages_container.get_message_by_uuid(op.item.id)
                if tw is None:
                    await self._messages_container.mount_messages(build_tool_message(op.item, self._item_presenters))
                else:
                    update_tool_message(check.isinstance(tw, ToolMessage), op.item, self._item_presenters)

            else:
                raise TypeError(op)

        await flush_stream_parts()

    _display_ops_task: asyncio.Task[None] | None = None

    @logs.async_exception_logging(alog, BaseException)
    async def _display_ops_task_main(self) -> None:
        # A dedicated consumer rather than pump-scheduled draining: display ops can be pushed before the app is fully
        # ready (e.g. window items right after attach), when pump-relative scheduling silently drops callbacks.
        while True:
            await self._display_ops_pending.wait()
            self._display_ops_pending.clear()

            await self._apply_display_ops(await self._display_op_relay.swap())

    ##
    # Timeline consumption

    _timeline_task: asyncio.Task[None] | None = None
    _timeline_attachment: mc.facades.timelines.TimelineAttachment | None = None

    _oldest_cursor: mc.facades.timelines.TimelineCursor | None = None
    _history_exhausted: bool = False
    _oldest_item_widget: Message | None = None

    @logs.async_exception_logging(alog, BaseException)
    async def _timeline_task_main(self) -> None:
        await self._chat_driver_started.wait()

        att = await self._timeline.attach(self._initial_timeline_window_limit)
        self._timeline_attachment = att

        self._oldest_cursor = att.window.before_cursor
        self._history_exhausted = not att.window.has_before

        for item in att.window.items:
            self._timeline_items_by_id[item.id] = item

            if (w := build_item_message(item, self._item_presenters)) is not None:
                if self._oldest_item_widget is None:
                    self._oldest_item_widget = w

                await self._display_op_relay.push(_MountWidgetDisplayOp(
                    w,
                    suppress_background_terminal_render=True,
                ))

        async for ev in att.subscription:
            await alog.debug(lambda: f'Got timeline event: {ev!r}')  # noqa

            await self._handle_timeline_event(ev)

    async def _handle_timeline_event(self, ev: mc.facades.timelines.TimelineEvent) -> None:
        if isinstance(ev, mc.facades.timelines.TimelineItemAppendedEvent):
            item = ev.item
            self._timeline_items_by_id[item.id] = item

            if isinstance(item, mc.facades.timelines.UserMessageTimelineItem):
                try:
                    self._no_echo_input_uuids.remove(item.id)
                except KeyError:
                    pass
                else:
                    return

            if (w := build_item_message(item, self._item_presenters)) is not None:
                await self._display_op_relay.push(_MountWidgetDisplayOp(w))

        elif isinstance(ev, mc.facades.timelines.TimelineItemDeltaEvent):
            old = self._timeline_items_by_id.get(ev.item_id)
            if old is None:
                return

            new = mc.facades.timelines.grow_streaming_item(old, ev.appended)
            self._timeline_items_by_id[ev.item_id] = new

            if isinstance(new, mc.facades.timelines.ToolUseTimelineItem):
                await self._display_op_relay.push(_UpdateToolDisplayOp(new))

            elif (cls := stream_message_cls_for_item(new)) is not None:
                await self._display_op_relay.push(ContentStreamMessagePart(
                    cls,
                    ev.item_id,
                    render_item_content_str(ev.appended),
                ))

        elif isinstance(ev, mc.facades.timelines.TimelineItemUpdatedEvent):
            item = ev.item
            old = self._timeline_items_by_id.get(item.id)
            self._timeline_items_by_id[item.id] = item

            if isinstance(item, mc.facades.timelines.ToolUseTimelineItem):
                await self._display_op_relay.push(_UpdateToolDisplayOp(item))

            elif old is not None and (old_cls := stream_message_cls_for_item(old)) is not None:
                # The canonical replacement (or errored finalization) of an in-flight stream item: its content has
                # already streamed into the widget - just finalize it.
                if item.finalized:
                    await self._display_op_relay.push(FinalStreamMessagePart(
                        old_cls,
                        item.id,
                    ))

            elif (w := build_item_message(item, self._item_presenters)) is not None and item.finalized:
                # An item form this frontend hasn't displayed yet (tolerance path).
                if self._messages_container.get_message_by_uuid(item.id) is None:
                    await self._display_op_relay.push(_MountWidgetDisplayOp(w))

    async def load_older_items(self, limit: int = 50) -> int:
        """
        Lazy scrollback: fetches the next older window and prepends its items above the current oldest. Returns the
        number of items loaded (0 once history is exhausted or before the attach completes).
        """

        if self._history_exhausted or (cursor := self._oldest_cursor) is None:
            return 0

        window = await self._timeline.get_before(cursor, limit)

        if window.before_cursor is not None:
            self._oldest_cursor = window.before_cursor
        self._history_exhausted = not window.has_before

        widgets: list[Message] = []
        for item in window.items:
            if item.id in self._timeline_items_by_id:
                continue  # window overlap - already displayed

            self._timeline_items_by_id[item.id] = item

            if (w := build_item_message(item, self._item_presenters)) is not None:
                widgets.append(w)

        if not widgets:
            return 0

        await self._display_op_relay.push(_MountWidgetsBeforeDisplayOp(
            tuple(widgets),
            self._oldest_item_widget,
        ))

        self._oldest_item_widget = widgets[0]

        return len(widgets)

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
        # Actions wait for driver startup: startup phase callbacks write storage, and concurrent write-bearing orm
        # sessions conflict under sqlite (see the start_driver note in on_mount).
        await self._chat_driver_started.wait()

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

            await alog.debug(lambda: f'Got chat action: {ac!r}')  # noqa

            if isinstance(ac, ChatDriverInterface.UserInput):
                await self._execute_chat_action(lambda: self.execute_user_input(ac))  # noqa

            else:
                raise TypeError(ac)  # noqa

    ##
    # Input

    async def send_user_input(self, s: str, *, no_echo: bool = False) -> None:
        input_uuid = uuid.uuid7()

        # The user message is *not* mounted here: it arrives as a timeline item (same uuid - the facade stamps it)
        # when the action begins. no_echo just marks that item to be skipped.
        if no_echo:
            self._no_echo_input_uuids.add(input_uuid)

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
