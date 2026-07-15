import typing as ta

from omcore import check
from omcore import resources as rs
from omcore.formats.json import all as json
from omcore.http import all as http

from .....core.http.sse import SseEvent
from .....core.http.sse import Utf8SseDecoder
from .....core.streams import StreamSink
from .....core.streams import new_stream
from ....types.backends import StreamBackend
from ....types.content import TextContentBuilder
from ....types.context import Context
from ....types.messages import AiMessage
from ....types.messages import AiMessageBuilder
from ....types.options import Options
from ....types.streams import AiStream
from ....types.streams import AiStreamEvent
from ....types.streams import StreamEndAiStreamEvent
from ....types.streams import StreamStartAiStreamEvent
from ....types.streams import TextDeltaAiStreamEvent
from ....types.streams import TextEndAiStreamEvent
from ....types.streams import TextStartAiStreamEvent
from ..base import BaseBackend
from .requests import RequestPreparer


##


def _stringify_error(error: ta.Any) -> str:
    if isinstance(error, str):
        return error
    try:
        return json.dumps(error)
    except (TypeError, ValueError):
        return str(error)


class SseEventProcessor:
    def __init__(self) -> None:
        super().__init__()

        self._message_builder = AiMessageBuilder()

    #

    def build_message(self) -> AiMessage:
        return self._message_builder.build()

    #

    _events_: list[AiStreamEvent] | None = None

    def _emit(self, event: AiStreamEvent) -> None:
        if (lst := self._events_) is None:
            lst = self._events_ = []
        lst.append(event)

    def _flush(self) -> list[AiStreamEvent]:
        ret, self._events_ = self._events_, []
        return ret or []

    #

    _text_builder_: TextContentBuilder | None = None

    def _text_builder(self) -> TextContentBuilder:
        if (b := self._text_builder_) is None:
            b = self._text_builder_ = TextContentBuilder()
            self._message_builder.content.append(b)
            self._emit(TextStartAiStreamEvent())
        return b

    #

    def _feed(self, sse: SseEvent) -> None:
        if sse.data == '[DONE]':
            return

        try:
            chunk = json.loads(sse.data)
        except (json.DecodeError, ValueError):
            return
        chunk = check.isinstance(chunk, ta.Mapping)

        if 'error' in chunk and chunk.get('error'):
            raise RuntimeError(_stringify_error(chunk['error']))

        choice = check.single(chunk['choices'])

        if (delta := choice.get('delta')) is None:
            return
        delta = check.isinstance(delta, ta.Mapping)

        if content := delta.get('content'):
            self._emit(TextDeltaAiStreamEvent(content))
            self._text_builder().text.write(content)

    def feed(self, sse: SseEvent) -> list[AiStreamEvent]:
        self._feed(sse)
        return self._flush()

    def _finish(self) -> None:
        for cb in self._message_builder.content:
            if isinstance(cb, TextContentBuilder):
                self._emit(TextEndAiStreamEvent(cb.build().text))

            else:
                raise TypeError(cb)

    def finish(self) -> list[AiStreamEvent]:
        self._finish()
        return self._flush()


##


class OpenaiCompletionsStreamBackend(BaseBackend, StreamBackend):
    async def stream(self, context: Context, options: Options | None = None) -> AiStream:
        raw_request = RequestPreparer(  # noqa
            self._model,
            context,
            options,
        ).raw_request()

        raw_request['stream'] = True

        #

        http_headers = {
            **({'authorization': f'Bearer {self._api_key.reveal()}'} if self._api_key is not None else {}),
            'content-type': 'application/json',
            'accept': 'application/json',
            **(self._model_http.extra_headers or {}),
        }

        http_request = http.HttpClientRequest(
            self._base_url + '/chat/completions',
            headers=http_headers,
            data=json.dumps(raw_request).encode('utf-8'),
        )

        #

        async with await rs.async_contextual_or_new(bind=True) as rm:  # noqa
            http_client = await rm.enter_async_context(http.manage_async_client(self._http_client))
            http_response = await rm.enter_async_context(await http_client.stream_request(http_request))

            if http_response.status != 200:
                err_http_response = await http.async_read_http_client_response(http_response)
                raise http.StatusHttpClientError(err_http_response)

            async def inner(sink: StreamSink[AiStreamEvent]) -> AiMessage:
                await sink.emit(StreamStartAiStreamEvent())

                decoder = Utf8SseDecoder()
                processor = SseEventProcessor()

                while read := await http_response.stream.read1():
                    for sse in decoder.feed(read):
                        for event in processor.feed(sse):
                            await sink.emit(event)

                for sse in decoder.finish():
                    for event in processor.feed(sse):
                        await sink.emit(event)

                for event in processor.finish():
                    await sink.emit(event)

                await sink.emit(StreamEndAiStreamEvent())

                return processor.build_message()

            return await new_stream(inner)
