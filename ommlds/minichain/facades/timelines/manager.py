"""
The translation pass from driver events to timeline state: an event-bus subscriber that owns a `TimelineState`, folds
every relevant event into it, and emits the resulting watermark-stamped `TimelineEvent`s back through the bus (where
subscription fan-out - and, incidentally, the JSONL event logger - pick them up).

The central move is *reconciliation*, exploiting the bus's event-ordering contract (streamy-talks-down: a successful
stream is always followed by an `AiMessagesEvent(streamed=True)` carrying the joined canonical messages, before any
tool execution events):

 - Stream deltas carry `MessageUuid`s, so in-flight items are created with ids equal to those uuids.
 - When the joined messages arrive, each one *replaces* its in-flight item - same id, advanced revision, canonical
   message-derived shape - converging live state onto exactly what later replay translation produces.
 - Joined `ToolUseMessage`s additionally record their tool-call-id -> item-id mapping, so the subsequent
   `ToolUseEvent`/`ToolUseResultEvent`s advance the *same* item through RUNNING to COMPLETE.

Stream items are deliberately *not* finalized on clean stream end - their replacement finalizes them. A stream end
carrying an exception is terminal (no canonical messages are coming): the in-flight item is finalized as-is with the
error (and a STREAMING tool item moves to FAILED).
"""
import uuid

from omlish import check
from omlish import dataclasses as dc

from ...chat.events import AiMessagesEvent
from ...chat.events import UserMessagesEvent
from ...chat.messages import Message
from ...chat.messages import ToolUseMessage
from ...chat.stream.events import AiStreamDeltaEvent
from ...chat.stream.events import AiStreamEndEvent
from ...chat.stream.types import ContentAiDelta
from ...chat.stream.types import PartialToolUseAiDelta
from ...chat.stream.types import ThinkingAiDelta
from ...chat.stream.types import ToolUseAiDelta
from ...events.manager import EventsManager
from ...events.types import ErrorEvent
from ...events.types import Event
from ...tools.execution.events import ToolUseEvent
from ...tools.execution.events import ToolUseResultEvent
from ...tools.types import ToolUse
from ..ui import UiMessageEvent
from .events import TimelineEvent
from .items import AiStreamTimelineItem
from .items import ErrorTimelineItem
from .items import ThinkingStreamTimelineItem
from .items import TimelineId
from .items import TimelineItem
from .items import TimelineItemId
from .items import ToolUseTimelineItem
from .items import ToolUseTimelineItemState
from .items import UiMessageTimelineItem
from .projection import grow_streaming_item
from .state import TimelineState
from .translate import timeline_item_id_for_message
from .translate import timeline_translate_message


##


class TimelineManager:
    def __init__(
            self,
            *,
            events: EventsManager,
            timeline_id: TimelineId | None = None,
            state: TimelineState | None = None,
    ) -> None:
        super().__init__()

        if state is None:
            state = TimelineState(
                timeline_id=timeline_id if timeline_id is not None else TimelineId(uuid.uuid7()),
            )
        elif timeline_id is not None:
            check.arg(state.timeline_id == timeline_id)

        self._events = events
        self._state = state

        self._tool_item_ids_by_use_key: dict[str, TimelineItemId] = {}

    @property
    def timeline_id(self) -> TimelineId:
        return self._state.timeline_id

    @property
    def state(self) -> TimelineState:
        return self._state

    ##
    # Internals

    async def _emit(self, event: TimelineEvent) -> None:
        await self._events.emit_event(event)

    @staticmethod
    def _tool_use_key(use: ToolUse) -> str:
        return use.id or use.name

    async def _append_canonical_message(self, message: Message) -> None:
        item = timeline_translate_message(message)

        if isinstance(message, ToolUseMessage):
            self._tool_item_ids_by_use_key[self._tool_use_key(message.tu)] = item.id

        await self._emit(self._state.append_item(item))

    async def _reconcile_canonical_message(self, message: Message) -> None:
        item_id = timeline_item_id_for_message(message)

        canonical = timeline_translate_message(message)

        if isinstance(message, ToolUseMessage):
            self._tool_item_ids_by_use_key[self._tool_use_key(message.tu)] = canonical.id

        if (existing := self._state.get_item(item_id)) is None:
            await self._emit(self._state.append_item(canonical))

        else:
            await self._emit(self._state.update_item(dc.replace(
                canonical,
                revision=existing.revision + 1,
            )))

    ##
    # Event handling

    async def handle_event(self, event: Event) -> None:
        if isinstance(event, TimelineEvent):
            return

        if isinstance(event, UserMessagesEvent):
            for user_msg in event.chat:
                await self._append_canonical_message(user_msg)

        elif isinstance(event, AiMessagesEvent):
            if event.streamed:
                for ai_msg in event.chat:
                    await self._reconcile_canonical_message(ai_msg)

            else:
                for ai_msg in event.chat:
                    await self._append_canonical_message(ai_msg)

        elif isinstance(event, AiStreamDeltaEvent):
            await self._handle_ai_stream_delta_event(event)

        elif isinstance(event, AiStreamEndEvent):
            await self._handle_ai_stream_end_event(event)

        elif isinstance(event, ToolUseEvent):
            await self._handle_tool_use_event(event)

        elif isinstance(event, ToolUseResultEvent):
            await self._handle_tool_use_result_event(event)

        elif isinstance(event, UiMessageEvent):
            await self._emit(self._state.append_item(UiMessageTimelineItem(
                text=event.text,
                finalized=True,
            )))

        elif isinstance(event, ErrorEvent):
            await self._emit(self._state.append_item(ErrorTimelineItem(
                message=event.message,
                error=event.error,
                finalized=True,
            )))

    ##
    # Streaming

    async def _handle_ai_stream_delta_event(self, event: AiStreamDeltaEvent) -> None:
        if (mu := event.message_uuid) is None:
            return

        item_id = TimelineItemId(mu)
        existing = self._state.get_item(item_id)
        delta = event.delta

        if isinstance(delta, ContentAiDelta):
            if existing is None:
                await self._emit(self._state.append_item(AiStreamTimelineItem(
                    id=item_id,
                    message_uuid=mu,
                    content=delta.c,
                )))

            elif isinstance(existing, AiStreamTimelineItem) and not existing.finalized:
                await self._emit(self._state.apply_item_delta(
                    grow_streaming_item(existing, delta.c),
                    delta.c,
                ))

        elif isinstance(delta, ThinkingAiDelta):
            if existing is None:
                await self._emit(self._state.append_item(ThinkingStreamTimelineItem(
                    id=item_id,
                    message_uuid=mu,
                    text=delta.c,
                )))

            elif isinstance(existing, ThinkingStreamTimelineItem) and not existing.finalized:
                await self._emit(self._state.apply_item_delta(
                    grow_streaming_item(existing, delta.c),
                    delta.c,
                ))

        elif isinstance(delta, PartialToolUseAiDelta):
            if existing is None:
                item = ToolUseTimelineItem(
                    id=item_id,
                    state=ToolUseTimelineItemState.STREAMING,
                    partial_name=delta.name,
                    partial_raw_args=delta.raw_args or None,
                )

                if delta.id is not None:
                    self._tool_item_ids_by_use_key[delta.id] = item_id

                await self._emit(self._state.append_item(item))

            elif (
                    isinstance(existing, ToolUseTimelineItem) and
                    existing.state is ToolUseTimelineItemState.STREAMING
            ):
                if delta.raw_args:
                    await self._emit(self._state.apply_item_delta(
                        grow_streaming_item(existing, delta.raw_args),
                        delta.raw_args,
                    ))

        elif isinstance(delta, ToolUseAiDelta):
            if existing is None:
                use = ToolUse(
                    id=delta.id,
                    name=check.non_empty_str(delta.name),
                    args=delta.args or {},
                )

                item = ToolUseTimelineItem(
                    id=item_id,
                    state=ToolUseTimelineItemState.PENDING,
                    use=use,
                )

                self._tool_item_ids_by_use_key[self._tool_use_key(use)] = item_id

                await self._emit(self._state.append_item(item))

    async def _handle_ai_stream_end_event(self, event: AiStreamEndEvent) -> None:
        if (mu := event.message_uuid) is None:
            return

        if event.exception is None:
            # Clean stream ends don't finalize in-flight items: the joined messages event that follows replaces (and
            # finalizes) them.
            return

        item = self._state.get_item(TimelineItemId(mu))
        if item is None or item.finalized:
            return

        new: TimelineItem

        if isinstance(item, (AiStreamTimelineItem, ThinkingStreamTimelineItem)):
            new = dc.replace(
                item,
                revision=item.revision + 1,
                error=event.exception,
                finalized=True,
            )

        elif isinstance(item, ToolUseTimelineItem) and item.state is ToolUseTimelineItemState.STREAMING:
            new = dc.replace(
                item,
                revision=item.revision + 1,
                state=ToolUseTimelineItemState.FAILED,
                error=event.exception,
                finalized=True,
            )

        else:
            return

        await self._emit(self._state.update_item(new))

    ##
    # Tool execution

    def _get_tool_item(self, use: ToolUse) -> ToolUseTimelineItem | None:
        if (item_id := self._tool_item_ids_by_use_key.get(self._tool_use_key(use))) is None:
            return None

        if not isinstance(item := self._state.get_item(item_id), ToolUseTimelineItem):
            return None

        return item

    async def _handle_tool_use_event(self, event: ToolUseEvent) -> None:
        if (existing := self._get_tool_item(event.use)) is not None:
            if existing.finalized:
                return

            await self._emit(self._state.update_item(dc.replace(
                existing,
                revision=existing.revision + 1,
                state=ToolUseTimelineItemState.RUNNING,
                # The message-derived use is kept where present - it is what replay translation will reproduce.
                use=existing.use if existing.use is not None else event.use,
                execution=event.tue,
            )))

            return

        item = ToolUseTimelineItem(
            state=ToolUseTimelineItemState.RUNNING,
            use=event.use,
            execution=event.tue,
        )

        self._tool_item_ids_by_use_key[self._tool_use_key(event.use)] = item.id

        await self._emit(self._state.append_item(item))

    async def _handle_tool_use_result_event(self, event: ToolUseResultEvent) -> None:
        if (existing := self._get_tool_item(event.use)) is not None:
            if existing.finalized:
                return

            await self._emit(self._state.update_item(dc.replace(
                existing,
                revision=existing.revision + 1,
                state=ToolUseTimelineItemState.COMPLETE,
                use=existing.use if existing.use is not None else event.use,
                result=event.tur,
                execution=event.tue if event.tue is not None else existing.execution,
                finalized=True,
            )))

            return

        item = ToolUseTimelineItem(
            state=ToolUseTimelineItemState.COMPLETE,
            use=event.use,
            result=event.tur,
            execution=event.tue,
            finalized=True,
        )

        self._tool_item_ids_by_use_key[self._tool_use_key(event.use)] = item.id

        await self._emit(self._state.append_item(item))
