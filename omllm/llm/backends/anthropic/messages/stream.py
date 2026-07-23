import typing as ta

from omcore import check
from omcore import resources as rs
from omcore.formats.json import all as json
from omcore.http import all as http

from .....core.http.sse import SseEvent
from ....types.backends import StreamBackend
from ....types.context import Context
from ....types.options import Options
from ....types.streams import AiStream
from ....types.streams import TextDeltaAiStreamEvent
from ....types.streams import ToolCallDeltaAiStreamEvent
from ...base.http import BaseHttpBackend
from ...base.sse import BaseBackendSseEventProcessor
from .requests import RequestPreparer


##


def _stringify_error(error: ta.Any) -> str:
    if isinstance(error, str):
        return error
    try:
        return json.dumps(error)
    except (TypeError, ValueError):
        return str(error)


class SseEventProcessor(BaseBackendSseEventProcessor):
    def _feed(self, sse: SseEvent) -> None:
        if sse.data == '[DONE]':
            return

        try:
            raw_chunk = json.loads(sse.data)
        except (json.DecodeError, ValueError):
            return
        raw_chunk = check.isinstance(raw_chunk, ta.Mapping)

        if 'error' in raw_chunk and raw_chunk.get('error'):
            raise RuntimeError(_stringify_error(raw_chunk['error']))

        raw_choice = check.single(raw_chunk['choices'])

        if (raw_delta := raw_choice.get('delta')) is None:
            return
        raw_delta = check.isinstance(raw_delta, ta.Mapping)

        if raw_content := raw_delta.get('content'):
            text = self._text()
            self._emit(TextDeltaAiStreamEvent(
                raw_content,
                content_index=self._content_index(text),
            ))
            text.text.write(raw_content)

        if raw_tool_calls := raw_delta.get('tool_calls'):
            for raw_tool_call in raw_tool_calls:  # noqa
                tool_call = self._tool_call(  # noqa
                    id=check.isinstance(raw_tool_call.get('id'), (str, None)),
                    index=check.isinstance(raw_tool_call.get('index'), (int, None)),
                )

                raw_fn = raw_tool_call.get('function') or {}
                if not tool_call.name and (raw_fn_name := raw_fn.get('name')):
                    tool_call.name = raw_fn_name

                args_delta = ''
                if raw_args := raw_fn.get('arguments'):
                    args_delta = check.isinstance(raw_args, str)
                    tool_call.partial_args.write(args_delta)
                    tool_call.parse_args()

                self._emit(ToolCallDeltaAiStreamEvent(
                    args_delta,
                    content_index=self._content_index(tool_call),
                ))


##


class AnthropicMessagesStreamBackend(BaseHttpBackend, StreamBackend):
    async def stream(self, context: Context, options: Options | None = None) -> AiStream:
        raw_request = RequestPreparer(  # noqa
            self._model,
            context,
            options,
        ).raw_request()

        raw_request['stream'] = True

        #

        http_headers = {
            **({'x-api-key': self._api_key.reveal()} if self._api_key is not None else {}),
            'content-type': 'application/json',
            'accept': 'application/json',
            **(self._model_http.extra_headers or {}),
        }

        http_request = http.HttpClientRequest(
            self._base_url + '/messages',
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

            processor = SseEventProcessor()

            return await processor.stream_http_response(http_response)
