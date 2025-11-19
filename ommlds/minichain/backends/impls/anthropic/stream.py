import typing as ta

from omlish import check
from omlish import marshal as msh
from omlish import typedvalues as tv
from omlish.formats import json
from omlish.http import all as http
from omlish.http import sse
from omlish.io.buffers import DelimitingBuffer

from .....backends.anthropic.protocol import types as pt
from .....backends.anthropic.protocol.sse.events import AnthropicSseDecoderEvents
from ....chat.choices.services import ChatChoicesOutputs
from ....chat.choices.stream.services import ChatChoicesStreamRequest
from ....chat.choices.stream.services import ChatChoicesStreamResponse
from ....chat.choices.stream.services import static_check_is_chat_choices_stream_service
from ....chat.choices.stream.types import AiChoiceDeltas
from ....chat.choices.stream.types import AiChoicesDeltas
from ....chat.stream.types import ContentAiDelta
from ....chat.stream.types import PartialToolUseAiDelta
from ....chat.tools.types import Tool
from ....configs import Config
from ....resources import UseResources
from ....standard import ApiKey
from ....stream.services import StreamResponseSink
from ....stream.services import new_stream_response
from .chat import AnthropicChatChoicesService
from .names import MODEL_NAMES
from .protocol import build_protocol_chat_messages
from .protocol import build_protocol_tool


##


# @omlish-manifest $.minichain.registries.manifests.RegistryManifest(
#     name='anthropic',
#     type='ChatChoicesStreamService',
# )
@static_check_is_chat_choices_stream_service
class AnthropicChatChoicesStreamService:
    def __init__(
            self,
            *configs: Config,
            http_client: http.AsyncHttpClient | None = None,
    ) -> None:
        super().__init__()

        self._http_client = http_client

        with tv.consume(*configs) as cc:
            self._model_name = cc.pop(AnthropicChatChoicesService.DEFAULT_MODEL_NAME)
            self._api_key = check.not_none(ApiKey.pop_secret(cc, env='ANTHROPIC_API_KEY'))

    READ_CHUNK_SIZE: ta.ClassVar[int] = -1

    async def invoke(
            self,
            request: ChatChoicesStreamRequest,
            *,
            max_tokens: int = 4096,  # FIXME: ChatOption
    ) -> ChatChoicesStreamResponse:
        messages, system = build_protocol_chat_messages(request.v)

        tools: list[pt.ToolSpec] = []
        with tv.TypedValues(*request.options).consume() as oc:
            t: Tool
            for t in oc.pop(Tool, []):
                tools.append(build_protocol_tool(t))

        a_req = pt.MessagesRequest(
            model=MODEL_NAMES.resolve(self._model_name.v),
            system=system,
            messages=messages,
            tools=tools or None,
            max_tokens=max_tokens,
            stream=True,
        )

        raw_request = msh.marshal(a_req)

        http_request = http.HttpRequest(
            'https://api.anthropic.com/v1/messages',
            headers={
                http.consts.HEADER_CONTENT_TYPE: http.consts.CONTENT_TYPE_JSON,
                b'x-api-key': self._api_key.reveal().encode('utf-8'),
                b'anthropic-version': b'2023-06-01',
            },
            data=json.dumps(raw_request).encode('utf-8'),
        )

        async with UseResources.or_new(request.options) as rs:
            http_client = await rs.enter_async_context(http.manage_async_client(self._http_client))
            http_response = await rs.enter_async_context(await http_client.stream_request(http_request))

            async def inner(sink: StreamResponseSink[AiChoicesDeltas]) -> ta.Sequence[ChatChoicesOutputs] | None:
                msg_start: AnthropicSseDecoderEvents.MessageStart | None = None
                cbk_start: AnthropicSseDecoderEvents.ContentBlockStart | None = None
                msg_stop: AnthropicSseDecoderEvents.MessageStop | None = None

                db = DelimitingBuffer([b'\r', b'\n', b'\r\n'])
                sd = sse.SseDecoder()
                while True:
                    b = await http_response.stream.read1(self.READ_CHUNK_SIZE)
                    for l in db.feed(b):
                        if isinstance(l, DelimitingBuffer.Incomplete):
                            # FIXME: handle
                            return []

                        # FIXME: https://docs.anthropic.com/en/docs/build-with-claude/streaming
                        for so in sd.process_line(l):
                            if isinstance(so, sse.SseEvent):
                                ss = so.data.decode('utf-8')
                                if ss == '[DONE]':
                                    return []

                                dct = json.loads(ss)
                                check.equal(dct['type'], so.type.decode('utf-8'))
                                ae = msh.unmarshal(dct, AnthropicSseDecoderEvents.Event)

                                match ae:
                                    case AnthropicSseDecoderEvents.MessageStart():
                                        check.none(msg_start)
                                        msg_start = ae
                                        if msg_start.message.content:
                                            raise NotImplementedError

                                    case AnthropicSseDecoderEvents.ContentBlockStart():
                                        check.not_none(msg_start)
                                        check.none(cbk_start)
                                        cbk_start = ae

                                        if isinstance(ae.content_block, AnthropicSseDecoderEvents.ContentBlockStart.Text):  # noqa
                                            await sink.emit(AiChoicesDeltas([AiChoiceDeltas([ContentAiDelta(
                                                ae.content_block.text,
                                            )])]))

                                        elif isinstance(ae.content_block, AnthropicSseDecoderEvents.ContentBlockStart.ToolUse):  # noqa
                                            await sink.emit(AiChoicesDeltas([AiChoiceDeltas([PartialToolUseAiDelta(  # noqa
                                                id=ae.content_block.id,
                                                name=ae.content_block.name,
                                                raw_args=ae.content_block.input,
                                            )])]))

                                        else:
                                            raise TypeError(ae.content_block)

                                    case AnthropicSseDecoderEvents.ContentBlockDelta():
                                        check.not_none(cbk_start)

                                        if isinstance(ae.delta, AnthropicSseDecoderEvents.ContentBlockDelta.TextDelta):
                                            await sink.emit(AiChoicesDeltas([AiChoiceDeltas([ContentAiDelta(
                                                ae.delta.text,
                                            )])]))

                                        elif isinstance(ae.delta, AnthropicSseDecoderEvents.ContentBlockDelta.InputJsonDelta):  # noqa
                                            await sink.emit(AiChoicesDeltas([AiChoiceDeltas([PartialToolUseAiDelta(  # noqa
                                                raw_args=ae.delta.partial_json,
                                            )])]))

                                        else:
                                            raise TypeError(ae.delta)

                                    case AnthropicSseDecoderEvents.ContentBlockStop():
                                        check.not_none(cbk_start)
                                        cbk_start = None

                                    case AnthropicSseDecoderEvents.MessageDelta():
                                        check.not_none(msg_start)
                                        check.none(cbk_start)

                                    case AnthropicSseDecoderEvents.MessageStop():
                                        check.not_none(msg_start)
                                        check.none(msg_stop)
                                        msg_stop = ae

                                    case AnthropicSseDecoderEvents.Ping():
                                        pass

                                    case _:
                                        raise TypeError(ae)

                    if not b:
                        check.not_none(msg_stop)
                        check.none(cbk_start)
                        return []

            # raw_response = json.loads(check.not_none(http_response.data).decode('utf-8'))
            # return rh.build_response(raw_response)

            return await new_stream_response(rs, inner)
