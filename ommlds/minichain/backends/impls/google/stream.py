"""
https://cloud.google.com/vertex-ai/generative-ai/docs/learn/models
"""
import typing as ta

from omlish import check
from omlish import marshal as msh
from omlish import typedvalues as tv
from omlish.formats import json
from omlish.http import all as http
from omlish.io.buffers import DelimitingBuffer

from .....backends.google.protocol import types as pt
from ....chat.choices.stream.services import ChatChoicesStreamRequest
from ....chat.choices.stream.services import ChatChoicesStreamResponse
from ....chat.choices.stream.services import static_check_is_chat_choices_stream_service
from ....chat.choices.stream.types import AiChoiceDeltas
from ....chat.choices.stream.types import AiChoicesDeltas
from ....chat.choices.types import ChatChoicesOutputs
from ....chat.messages import AiMessage
from ....chat.messages import Message
from ....chat.messages import SystemMessage
from ....chat.messages import ToolUseMessage
from ....chat.messages import ToolUseResultMessage
from ....chat.messages import UserMessage
from ....chat.stream.types import ContentAiDelta
from ....chat.stream.types import ToolUseAiDelta
from ....chat.tools.types import Tool
from ....models.configs import ModelName
from ....resources import UseResources
from ....standard import ApiKey
from ....stream.services import StreamResponseSink
from ....stream.services import new_stream_response
from .names import MODEL_NAMES
from .tools import build_tool_spec_schema


##


# @omlish-manifest $.minichain.registries.manifests.RegistryManifest(
#     name='google',
#     type='ChatChoicesStreamService',
# )
@static_check_is_chat_choices_stream_service
class GoogleChatChoicesStreamService:
    DEFAULT_MODEL_NAME: ta.ClassVar[ModelName] = ModelName(check.not_none(MODEL_NAMES.default))

    def __init__(
            self,
            *configs: ApiKey | ModelName,
            http_client: http.AsyncHttpClient | None = None,
    ) -> None:
        super().__init__()

        self._http_client = http_client

        with tv.consume(*configs) as cc:
            self._model_name = cc.pop(self.DEFAULT_MODEL_NAME)
            self._api_key = ApiKey.pop_secret(cc, env='GEMINI_API_KEY')

    def _make_str_content(
            self,
            s: str | None,
            *,
            role: pt.ContentRole | None = None,
    ) -> pt.Content | None:
        if s is None:
            return None

        return pt.Content(
            parts=[pt.Part(
                text=check.not_none(s),
            )],
            role=role,
        )

    def _make_msg_content(self, m: Message) -> pt.Content:
        if isinstance(m, (AiMessage, SystemMessage, UserMessage)):
            return check.not_none(self._make_str_content(
                check.isinstance(m.c, str),
                role=self.ROLES_MAP[type(m)],
            ))

        elif isinstance(m, ToolUseResultMessage):
            tr_resp_val: pt.Value
            if m.tur.c is None:
                tr_resp_val = pt.NullValue()  # type: ignore[unreachable]
            elif isinstance(m.tur.c, str):
                tr_resp_val = pt.StringValue(m.tur.c)
            else:
                raise TypeError(m.tur.c)
            return pt.Content(
                parts=[pt.Part(
                    function_response=pt.FunctionResponse(
                        id=m.tur.id,
                        name=m.tur.name,
                        response={
                            'value': tr_resp_val,
                        },
                    ),
                )],
            )

        elif isinstance(m, ToolUseMessage):
            return pt.Content(
                parts=[pt.Part(
                    function_call=pt.FunctionCall(
                        id=m.tu.id,
                        name=m.tu.name,
                        args=m.tu.args,
                    ),
                )],
                role='model',
            )

        else:
            raise TypeError(m)

    BASE_URL: ta.ClassVar[str] = 'https://generativelanguage.googleapis.com/v1beta/models'

    ROLES_MAP: ta.ClassVar[ta.Mapping[type[Message], pt.ContentRole | None]] = {  # noqa
        SystemMessage: None,
        UserMessage: 'user',
        AiMessage: 'model',
    }

    READ_CHUNK_SIZE: ta.ClassVar[int] = -1

    async def invoke(
            self,
            request: ChatChoicesStreamRequest,
    ) -> ChatChoicesStreamResponse:
        key = check.not_none(self._api_key).reveal()

        msgs = list(request.v)

        system_inst: pt.Content | None = None
        if msgs and isinstance(m0 := msgs[0], SystemMessage):
            system_inst = self._make_msg_content(m0)
            msgs.pop(0)

        g_tools: list[pt.Tool] = []
        with tv.TypedValues(*request.options).consume() as oc:
            t: Tool
            for t in oc.pop(Tool, []):
                g_tools.append(pt.Tool(
                    function_declarations=[build_tool_spec_schema(t.spec)],
                ))

        g_req = pt.GenerateContentRequest(
            contents=[
                self._make_msg_content(m)
                for m in msgs
            ],
            tools=g_tools or None,
            system_instruction=system_inst,
        )

        req_dct = msh.marshal(g_req)

        model_name = MODEL_NAMES.resolve(self._model_name.v)

        http_request = http.HttpRequest(
            f'{self.BASE_URL.rstrip("/")}/{model_name}:streamGenerateContent?alt=sse&key={key}',
            headers={'Content-Type': 'application/json'},
            data=json.dumps_compact(req_dct).encode('utf-8'),
            method='POST',
        )

        async with UseResources.or_new(request.options) as rs:
            http_client = await rs.enter_async_context(http.manage_async_client(self._http_client))
            http_response = await rs.enter_async_context(await http_client.stream_request(http_request))

            async def inner(sink: StreamResponseSink[AiChoicesDeltas]) -> ta.Sequence[ChatChoicesOutputs] | None:
                db = DelimitingBuffer([b'\r', b'\n', b'\r\n'])
                while True:
                    b = await http_response.stream.read1(self.READ_CHUNK_SIZE)
                    for bl in db.feed(b):
                        if isinstance(bl, DelimitingBuffer.Incomplete):
                            # FIXME: handle
                            return []

                        l = bl.decode('utf-8')
                        if not l:
                            continue

                        if l.startswith('data: '):
                            gcr = msh.unmarshal(json.loads(l[6:]), pt.GenerateContentResponse)  # noqa
                            cnd = check.single(check.not_none(gcr.candidates))

                            for p in check.not_none(cnd.content).parts or []:
                                if (txt := p.text) is not None:
                                    check.none(p.function_call)
                                    await sink.emit(AiChoicesDeltas([
                                        AiChoiceDeltas([
                                            ContentAiDelta(check.not_none(txt)),
                                        ]),
                                    ]))

                                elif (fc := p.function_call) is not None:
                                    check.none(p.text)
                                    await sink.emit(AiChoicesDeltas([
                                        AiChoiceDeltas([
                                            ToolUseAiDelta(
                                                id=fc.id,
                                                name=fc.name,
                                                args=fc.args,
                                            ),
                                        ]),
                                    ]))

                                else:
                                    raise ValueError(p)

                    if not b:
                        return []

            return await new_stream_response(rs, inner)
