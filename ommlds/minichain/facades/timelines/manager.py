import uuid

from omlish import dataclasses as dc

from ...chat.events import AiMessagesEvent
from ...chat.events import UserMessagesEvent
from ...chat.messages import Message
from ...chat.messages import ToolUseMessage
from ...chat.stream.events import AiStreamBeginEvent
from ...chat.stream.events import AiStreamDeltaEvent
from ...chat.stream.events import AiStreamEndEvent
from ...chat.stream.types import ContentAiDelta
from ...content.content import Content
from ...events.manager import EventsManager
from ...events.types import Event
from ...tools.execution.events import ToolUseEvent
from ...tools.execution.events import ToolUseResultEvent
from .events import TimelineEvent
from .history import StateTimelineHistory
from .items import AiStreamTimelineItem
from .items import TimelineId
from .items import TimelineItem
from .items import TimelineItemId
from .items import ToolUseTimelineItem
from .items import ToolUseTimelineItemState
from .messages import timeline_item_from_message
from .state import TimelineState
from .views import TimelineView


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

        if timeline_id is None:
            timeline_id = TimelineId(uuid.uuid7())

        self._events = events
        self._state = state if state is not None else TimelineState(timeline_id=timeline_id)
        self._view = TimelineView(history=StateTimelineHistory(state=self._state))

        self._stream_items_by_message_uuid: dict[uuid.UUID, TimelineItemId] = {}
        self._tool_items_by_use_key: dict[str, TimelineItemId] = {}

    @property
    def state(self) -> TimelineState:
        return self._state

    @property
    def view(self) -> TimelineView:
        return self._view

    #

    async def _emit(self, event: TimelineEvent) -> None:
        await self._events.emit_event(event)

    async def _append_item(self, item: TimelineItem) -> None:
        await self._emit(self._state.append_item(item))

    async def _update_item(self, item: TimelineItem) -> None:
        await self._emit(self._state.update_item(item))

    async def _finalize_item(self, item_id: TimelineItemId) -> None:
        await self._emit(self._state.finalize_item(item_id))

    #

    @staticmethod
    def _tool_use_key(ev: ToolUseEvent | ToolUseResultEvent) -> str:
        return ev.use.id or ev.use.name

    @staticmethod
    def _append_content(old: Content | None, new: Content) -> Content:
        if old is None:
            return new

        # FIXME:
        #  - lazy, collapse-on-access, linked-listy box thingy
        #  - also, like, resolve the fact deltas are only really defined for string concat'd markdown lol - non-lifted
        #    list content is intentionally undefined, configurably lifted to containers in
        #    LiftToStandardContentTransform

        if isinstance(old, str) and isinstance(new, str):
            return old + new

        return [old, new]

    async def _append_message(self, message: Message) -> None:
        item = timeline_item_from_message(message)

        if isinstance(message, ToolUseMessage):
            self._tool_items_by_use_key[message.tu.id or message.tu.name] = item.id

        await self._append_item(item)

    #

    async def handle_event(self, event: Event) -> None:
        if isinstance(event, TimelineEvent):
            return

        if isinstance(event, UserMessagesEvent):
            for user_msg in event.chat:
                await self._append_message(user_msg)

        elif isinstance(event, AiMessagesEvent):
            if not event.streamed:
                for ai_msg in event.chat:
                    await self._append_message(ai_msg)

        elif isinstance(event, AiStreamBeginEvent):
            if event.message_uuid is not None:
                item = AiStreamTimelineItem(
                    message_uuid=event.message_uuid,
                )

                self._stream_items_by_message_uuid[event.message_uuid] = item.id
                await self._append_item(item)

        elif isinstance(event, AiStreamDeltaEvent):
            await self._handle_ai_stream_delta_event(event)

        elif isinstance(event, AiStreamEndEvent):
            await self._handle_ai_stream_end_event(event)

        elif isinstance(event, ToolUseEvent):
            await self._handle_tool_use_event(event)

        elif isinstance(event, ToolUseResultEvent):
            await self._handle_tool_use_result_event(event)

    async def _handle_ai_stream_delta_event(self, event: AiStreamDeltaEvent) -> None:
        if event.message_uuid is None:
            return

        item_id = self._stream_items_by_message_uuid.get(event.message_uuid)
        if item_id is None:
            new_item = AiStreamTimelineItem(
                message_uuid=event.message_uuid,
            )

            self._stream_items_by_message_uuid[event.message_uuid] = new_item.id
            await self._append_item(new_item)

            item_id = new_item.id

        item = self._state.get_item(item_id)
        if not isinstance(item, AiStreamTimelineItem):
            return

        if isinstance(event.delta, ContentAiDelta):
            await self._update_item(dc.replace(
                item,
                revision=item.revision + 1,
                content=self._append_content(item.content, event.delta.c),
            ))

    async def _handle_ai_stream_end_event(self, event: AiStreamEndEvent) -> None:
        if event.message_uuid is None:
            return

        item_id = self._stream_items_by_message_uuid.get(event.message_uuid)
        if item_id is None:
            return

        item = self._state.get_item(item_id)
        if not isinstance(item, AiStreamTimelineItem):
            return

        if event.exception is not None:
            await self._update_item(dc.replace(
                item,
                revision=item.revision + 1,
                error=event.exception,
            ))

        await self._finalize_item(item_id)

    async def _handle_tool_use_event(self, event: ToolUseEvent) -> None:
        key = self._tool_use_key(event)

        item_id = self._tool_items_by_use_key.get(key)
        if item_id is not None and isinstance(item := self._state.get_item(item_id), ToolUseTimelineItem):
            await self._update_item(dc.replace(
                item,
                revision=item.revision + 1,
                state=ToolUseTimelineItemState.RUNNING,
                execution=event.tue,
            ))
            return

        item = ToolUseTimelineItem(
            use=event.use,
            state=ToolUseTimelineItemState.RUNNING,
            execution=event.tue,
        )

        self._tool_items_by_use_key[key] = item.id
        await self._append_item(item)

    async def _handle_tool_use_result_event(self, event: ToolUseResultEvent) -> None:
        key = self._tool_use_key(event)

        item_id = self._tool_items_by_use_key.get(key)
        if item_id is None:
            new_item = ToolUseTimelineItem(
                use=event.use,
                state=ToolUseTimelineItemState.COMPLETE,
                result=event.tur,
                execution=event.tue,
                finalized=True,
            )

            self._tool_items_by_use_key[key] = new_item.id
            await self._append_item(new_item)
            return

        item = self._state.get_item(item_id)
        if not isinstance(item, ToolUseTimelineItem):
            return

        await self._update_item(dc.replace(
            item,
            revision=item.revision + 1,
            state=ToolUseTimelineItemState.COMPLETE,
            result=event.tur,
            execution=event.tue,
            finalized=True,
        ))
