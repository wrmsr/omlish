"""
https://cloud.google.com/vertex-ai/generative-ai/docs/learn/models
"""
import typing as ta

from omlish import check
from omlish import marshal as msh
from omlish import typedvalues as tv
from omlish.formats import json
from omlish.http import all as http

from .....backends.google.protocol import types as pt
from ....chat.choices.services import ChatChoicesRequest
from ....chat.choices.services import ChatChoicesResponse
from ....chat.choices.services import static_check_is_chat_choices_service
from ....chat.choices.types import AiChoice
from ....chat.messages import AiMessage
from ....chat.messages import AnyAiMessage
from ....chat.messages import Message
from ....chat.messages import SystemMessage
from ....chat.messages import ToolUseMessage
from ....chat.messages import ToolUseResultMessage
from ....chat.messages import UserMessage
from ....chat.tools.types import Tool
from ....models.configs import ModelName
from ....standard import ApiKey
from ....tools.types import ToolUse
from .names import MODEL_NAMES
from .tools import build_tool_spec_schema


##


# @omlish-manifest $.minichain.registries.manifests.RegistryManifest(
#     name='google',
#     type='ChatChoicesService',
# )
@static_check_is_chat_choices_service
class GoogleChatChoicesService:
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

    def _get_msg_content(self, m: Message) -> str | None:
        if isinstance(m, AiMessage):
            return check.isinstance(m.c, str)

        elif isinstance(m, (SystemMessage, UserMessage)):
            return check.isinstance(m.c, str)

        else:
            raise TypeError(m)

    BASE_URL: ta.ClassVar[str] = 'https://generativelanguage.googleapis.com/v1beta/models'

    ROLES_MAP: ta.ClassVar[ta.Mapping[type[Message], str]] = {
        UserMessage: 'user',
        AiMessage: 'model',
        ToolUseMessage: 'model',
    }

    async def invoke(
            self,
            request: ChatChoicesRequest,
    ) -> ChatChoicesResponse:
        key = check.not_none(self._api_key).reveal()

        g_sys_content: pt.Content | None = None
        g_contents: list[pt.Content] = []
        for i, m in enumerate(request.v):
            if isinstance(m, SystemMessage):
                check.arg(i == 0)
                check.none(g_sys_content)
                g_sys_content = pt.Content(
                    parts=[pt.Part(
                        text=check.not_none(self._get_msg_content(m)),
                    )],
                )

            elif isinstance(m, ToolUseResultMessage):
                tr_resp_val: pt.Value
                if m.tur.c is None:
                    tr_resp_val = pt.NullValue()  # type: ignore[unreachable]
                elif isinstance(m.tur.c, str):
                    tr_resp_val = pt.StringValue(m.tur.c)
                else:
                    raise TypeError(m.tur.c)
                g_contents.append(pt.Content(
                    parts=[pt.Part(
                        function_response=pt.FunctionResponse(
                            id=m.tur.id,
                            name=m.tur.name,
                            response={
                                'value': tr_resp_val,
                            },
                        ),
                    )],
                ))

            elif isinstance(m, AiMessage):
                g_contents.append(pt.Content(
                    parts=[pt.Part(
                        text=check.not_none(self._get_msg_content(m)),
                    )],
                    role='model',
                ))

            elif isinstance(m, ToolUseMessage):
                g_contents.append(pt.Content(
                    parts=[pt.Part(
                        function_call=pt.FunctionCall(
                            id=m.tu.id,
                            name=m.tu.name,
                            args=m.tu.args,
                        ),
                    )],
                    role='model',
                ))

            else:
                g_contents.append(pt.Content(
                    parts=[pt.Part(
                        text=check.not_none(self._get_msg_content(m)),
                    )],
                    role=self.ROLES_MAP[type(m)],  # type: ignore[arg-type]
                ))

        g_tools: list[pt.Tool] = []
        with tv.TypedValues(*request.options).consume() as oc:
            t: Tool
            for t in oc.pop(Tool, []):
                g_tools.append(pt.Tool(
                    function_declarations=[build_tool_spec_schema(t.spec)],
                ))

        g_req = pt.GenerateContentRequest(
            contents=g_contents or None,
            tools=g_tools or None,
            system_instruction=g_sys_content,
        )

        req_dct = msh.marshal(g_req)

        model_name = MODEL_NAMES.resolve(self._model_name.v)

        resp = await http.async_request(
            f'{self.BASE_URL.rstrip("/")}/{model_name}:generateContent?key={key}',
            headers={'Content-Type': 'application/json'},
            data=json.dumps_compact(req_dct).encode('utf-8'),
            method='POST',
            client=self._http_client,
        )

        resp_dct = json.loads(check.not_none(resp.data).decode('utf-8'))

        g_resp = msh.unmarshal(resp_dct, pt.GenerateContentResponse)

        ai_choices: list[AiChoice] = []
        for c in g_resp.candidates or []:
            out: list[AnyAiMessage] = []
            for g_resp_part in check.not_none(check.not_none(c.content).parts):
                if (g_txt := g_resp_part.text) is not None:
                    out.append(AiMessage(g_txt))
                elif (g_fc := g_resp_part.function_call) is not None:
                    out.append(ToolUseMessage(ToolUse(
                        id=g_fc.id,
                        name=g_fc.name,
                        args=g_fc.args or {},
                    )))
                else:
                    raise TypeError(g_resp_part)
            ai_choices.append(AiChoice(out))

        return ChatChoicesResponse(ai_choices)
