"""
The bare frontend's timeline consumer: one event-bus callback rendering `TimelineEvent`s to the printing layer,
replacing the old per-driver-event printers. Linear/append-only semantics: finalized items print whole, the in-flight
prose tail streams through a print context, and tool cards print as state-transition lines. The
streamed-vs-joined-event rule lives in the timeline manager now - not here.

Deliberately synchronous with the bus (no subscription task): oneshot runs print everything before `do_action`
returns, and nothing here can lag the driver.
"""
import functools
import typing as ta

from omlish import check

from ..... import minichain as mc
from ....interfaces.bare.printing.types import ContentPrinting
from ....interfaces.bare.printing.types import StreamContentPrinting


##


class TimelineEventPrinter:
    def __init__(
            self,
            *,
            printer: ContentPrinting,
            stream_printer: StreamContentPrinting,
            print_user_messages: bool = False,
            print_thinking: bool = False,
            print_tool_use: bool = False,
    ) -> None:
        super().__init__()

        self._printer = printer
        self._stream_printer = stream_printer
        self._print_user_messages = print_user_messages
        self._print_thinking = print_thinking
        self._print_tool_use = print_tool_use

        self._items_by_id: dict[mc.facades.timelines.TimelineItemId, mc.facades.timelines.TimelineItem] = {}

        self._open_stream_item_id: mc.facades.timelines.TimelineItemId | None = None
        self._open_stream_ctx: ContentPrinting | None = None
        self._close_stream_ctx: ta.Callable[[], ta.Awaitable[ta.Any]] | None = None

    ##
    # The streaming print context - one open at a time (deltas for one item are contiguous in practice).

    async def _open_stream(self, item_id: mc.facades.timelines.TimelineItemId) -> ContentPrinting:
        await self._close_stream()

        acm = self._stream_printer.create_context()
        self._open_stream_ctx = await acm.__aenter__()
        self._close_stream_ctx = functools.partial(acm.__aexit__, None, None, None)
        self._open_stream_item_id = item_id

        return self._open_stream_ctx

    async def _close_stream(self) -> None:
        if (cs := self._close_stream_ctx) is None:
            return

        self._open_stream_item_id = None
        self._open_stream_ctx = None
        self._close_stream_ctx = None

        await cs()

    ##
    # Item rendering

    def _should_stream_item(self, item: mc.facades.timelines.TimelineItem) -> bool:
        if isinstance(item, mc.facades.timelines.AiStreamTimelineItem):
            return True

        if isinstance(item, mc.facades.timelines.ThinkingStreamTimelineItem):
            return self._print_thinking

        return False

    def _streamed_item_text(self, item: mc.facades.timelines.TimelineItem) -> mc.Content | None:
        if isinstance(item, mc.facades.timelines.AiStreamTimelineItem):
            return item.content

        elif isinstance(item, mc.facades.timelines.ThinkingStreamTimelineItem):
            return item.text

        else:
            return None

    async def _print_whole_item(self, item: mc.facades.timelines.TimelineItem) -> None:
        if isinstance(item, mc.facades.timelines.UserMessageTimelineItem):
            if self._print_user_messages:
                await self._printer.print_content(item.message.c)

        elif isinstance(item, mc.facades.timelines.AiMessageTimelineItem):
            if item.message.c is not None:
                await self._printer.print_content(item.message.c)

        elif isinstance(item, mc.facades.timelines.ThinkingTimelineItem):
            if self._print_thinking:
                await self._printer.print_content(item.message.c)

        elif isinstance(item, mc.facades.timelines.UiMessageTimelineItem):
            await self._printer.print_content(str(item.text))

        elif isinstance(item, mc.facades.timelines.ErrorTimelineItem):
            await self._printer.print_content(mc.JsonContent(dict(
                error=item.message if item.message is not None else repr(item.error),
            )))

    async def _print_tool_transition(
            self,
            old: mc.facades.timelines.ToolUseTimelineItem | None,
            new: mc.facades.timelines.ToolUseTimelineItem,
    ) -> None:
        if not self._print_tool_use:
            return

        old_state = old.state if old is not None else None
        if new.state is old_state:
            return

        if new.state is mc.facades.timelines.ToolUseTimelineItemState.RUNNING:
            use = check.not_none(new.use)
            await self._printer.print_content(mc.JsonContent(dict(
                id=use.id,
                name=use.name,
                args=use.args,
            )))

        elif new.state is mc.facades.timelines.ToolUseTimelineItemState.COMPLETE:
            await self._printer.print_content(check.not_none(new.result).c)

        elif new.state in (
                mc.facades.timelines.ToolUseTimelineItemState.FAILED,
                mc.facades.timelines.ToolUseTimelineItemState.DENIED,
        ):
            await self._printer.print_content(mc.JsonContent(dict(
                tool=new.partial_name if new.use is None else new.use.name,
                state=str(new.state),
                error=repr(new.error) if new.error is not None else None,
            )))

    ##
    # Event handling

    async def handle_event(self, event: mc.Event) -> None:
        if not isinstance(event, mc.facades.timelines.TimelineEvent):
            return

        if isinstance(event, mc.facades.timelines.TimelineItemAppendedEvent):
            item = event.item
            self._items_by_id[item.id] = item

            if self._should_stream_item(item):
                ctx = await self._open_stream(item.id)
                if (c := self._streamed_item_text(item)) is not None:
                    await ctx.print_content(c)

            elif isinstance(item, mc.facades.timelines.ToolUseTimelineItem):
                await self._print_tool_transition(None, item)

            elif item.finalized:
                await self._print_whole_item(item)

        elif isinstance(event, mc.facades.timelines.TimelineItemDeltaEvent):
            old = self._items_by_id.get(event.item_id)
            if old is None:
                return

            new = mc.facades.timelines.grow_streaming_item(old, event.appended)
            self._items_by_id[event.item_id] = new

            if event.item_id == self._open_stream_item_id and self._open_stream_ctx is not None:
                await self._open_stream_ctx.print_content(event.appended)

        elif isinstance(event, mc.facades.timelines.TimelineItemUpdatedEvent):
            item = event.item
            old = self._items_by_id.get(item.id)
            self._items_by_id[item.id] = item

            if item.id == self._open_stream_item_id:
                # The canonical replacement (or errored finalization) of the item being streamed - its content has
                # already been printed; just close the stream context.
                if item.finalized:
                    await self._close_stream()

            elif isinstance(item, mc.facades.timelines.ToolUseTimelineItem):
                await self._print_tool_transition(
                    old if isinstance(old, mc.facades.timelines.ToolUseTimelineItem) else None,
                    item,
                )

            elif item.finalized and old is not None and not old.finalized and not self._should_stream_item(old):
                # An item that went final without ever having streamed visibly (e.g. thinking with printing off
                # needs nothing; a non-streamed-visible item that finalizes prints whole).
                if not self._should_stream_item(item):
                    await self._print_whole_item(item)
