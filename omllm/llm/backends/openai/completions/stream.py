from omcore import resources as rs
from omcore.formats.json import all as json
from omcore.http import all as http

from .....core.http.sse import Utf8SseDecoder
from .....core.streams import StreamSink
from .....core.streams import new_stream
from ....types.backends import StreamBackend
from ....types.content import TextContent
from ....types.context import Context
from ....types.messages import AiMessage
from ....types.options import Options
from ....types.streams import AiEvent
from ....types.streams import AiStream
from ....types.streams import EndAiEvent
from ....types.streams import StartAiEvent
from ..base import BaseBackend
from .requests import RequestPreparer


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

            async def inner(sink: StreamSink[AiEvent]) -> AiMessage:
                await sink.emit(StartAiEvent())

                decoder = Utf8SseDecoder()

                while read := await http_response.stream.read1():
                    for item in decoder.feed(read):
                        print(item)

                for item in decoder.finish():
                    print(item)

                await sink.emit(EndAiEvent())

                return AiMessage([TextContent('FIXME')])

            return await new_stream(inner)
