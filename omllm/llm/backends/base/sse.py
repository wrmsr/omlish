import abc
import typing as ta

from omcore import check
from omcore import collections as col
from omcore.http import all as http

from ....core.http.sse import SseEvent
from ....core.http.sse import Utf8SseDecoder
from ....core.streams import StreamSink
from ....core.streams import new_stream
from ...types.content import ContentBuilder
from ...types.content import TextContentBuilder
from ...types.content import ToolCallBuilder
from ...types.messages import AiMessage
from ...types.messages import AiMessageBuilder
from ...types.streams import AiStream
from ...types.streams import AiStreamEvent
from ...types.streams import StreamEndAiStreamEvent
from ...types.streams import StreamStartAiStreamEvent
from ...types.streams import TextEndAiStreamEvent
from ...types.streams import TextStartAiStreamEvent
from ...types.streams import ToolCallEndAiStreamEvent
from ...types.streams import ToolCallStartAiStreamEvent


##


class BaseBackendSseEventProcessor:
    def __init__(self) -> None:
        super().__init__()

        self._message = AiMessageBuilder()

        self._events_: list[AiStreamEvent] = []

        self._content_indexes_: dict[ContentBuilder, int] = {}

        self._text_: TextContentBuilder | None = None

        self._tool_calls_by_id_: dict[str, ToolCallBuilder] = {}
        self._tool_calls_by_index_: col.MutableBiMap[int, ToolCallBuilder] = col.make_mutable_bi_map()

    #

    def build_message(self) -> AiMessage:
        return self._message.build()

    #

    def _emit(self, event: AiStreamEvent) -> None:
        self._events_.append(event)

    def _flush(self) -> list[AiStreamEvent]:
        ret, self._events_ = self._events_, []
        return ret or []

    #

    def _add_content(self, content: ContentBuilder) -> int:
        check.not_in(content, self._content_indexes_)
        i = len(self._message.content)
        self._message.content.append(ta.cast(ta.Any, content))
        self._content_indexes_[content] = i
        return i

    def _content_index(self, content: ContentBuilder) -> int:
        return self._content_indexes_[content]

    #

    def _text(self) -> TextContentBuilder:
        if (b := self._text_) is None:
            b = self._text_ = TextContentBuilder()
            i = self._add_content(b)
            self._emit(TextStartAiStreamEvent(
                content_index=i,
            ))
        return b

    #

    def _tool_call(
            self,
            *,
            id: str | None = None,  # noqa
            index: int | None = None,
    ) -> ToolCallBuilder:
        if id is not None and index is None:
            raise ValueError('id or index must be specified')

        if id is not None:
            if (b := self._tool_calls_by_id_.get(id)) is not None:
                if index is not None:
                    if (xb := self._tool_calls_by_index_.get(index)) is not None:
                        check.is_(b, xb)
                    else:
                        self._tool_calls_by_index_[index] = b
                return b

        if index is not None:
            if (b := self._tool_calls_by_index_.get(index)) is not None:
                if id is not None:
                    check.none(b.id)
                    check.not_in(id, self._tool_calls_by_id_)
                    b.id = id
                    self._tool_calls_by_id_[id] = b
                return b

        b = ToolCallBuilder()
        i = self._add_content(b)
        self._emit(ToolCallStartAiStreamEvent(
            content_index=i,
        ))

        if id is not None:
            b.id = id
            self._tool_calls_by_id_[id] = b

        if index is not None:
            self._tool_calls_by_index_[index] = b

        return b

    #

    @abc.abstractmethod
    def _feed(self, sse: SseEvent) -> None:
        raise NotImplementedError

    def feed(self, sse: SseEvent) -> list[AiStreamEvent]:
        self._feed(sse)
        return self._flush()

    def _finish(self) -> None:
        for content in self._message.content:
            if isinstance(content, TextContentBuilder):
                self._emit(TextEndAiStreamEvent(
                    content.build().text,
                    content_index=self._content_index(content),
                ))

            elif isinstance(content, ToolCallBuilder):
                self._emit(ToolCallEndAiStreamEvent(
                    content.build(),
                    content_index=self._content_index(content),
                ))

            else:
                raise TypeError(content)

    def finish(self) -> list[AiStreamEvent]:
        self._finish()
        return self._flush()

    #

    async def stream_http_response(
            self,
            http_response: http.AsyncStreamHttpClientResponse,
    ) -> AiStream:
        async def inner(sink: StreamSink[AiStreamEvent]) -> AiMessage:
            await sink.emit(StreamStartAiStreamEvent())

            decoder = Utf8SseDecoder()

            while read := await http_response.stream.read1():
                for sse in decoder.feed(read):
                    for event in self.feed(sse):
                        await sink.emit(event)

            for sse in decoder.finish():
                for event in self.feed(sse):
                    await sink.emit(event)

            for event in self.finish():
                await sink.emit(event)

            await sink.emit(StreamEndAiStreamEvent())

            return self.build_message()

        return await new_stream(inner)
