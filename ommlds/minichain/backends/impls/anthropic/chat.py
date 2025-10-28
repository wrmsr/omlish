"""
https://docs.claude.com/en/api/messages
https://github.com/anthropics/anthropic-sdk-python/tree/cd80d46f7a223a5493565d155da31b898a4c6ee5/src/anthropic/types
https://github.com/anthropics/anthropic-sdk-python/blob/cd80d46f7a223a5493565d155da31b898a4c6ee5/src/anthropic/resources/completions.py#L53
https://github.com/anthropics/anthropic-sdk-python/blob/cd80d46f7a223a5493565d155da31b898a4c6ee5/src/anthropic/resources/messages.py#L70
"""
import typing as ta

from omlish import check
from omlish import marshal as msh
from omlish import typedvalues as tv
from omlish.formats import json
from omlish.http import all as http

from .....backends.anthropic.protocol import types as pt
from ....chat.choices.services import ChatChoicesRequest
from ....chat.choices.services import ChatChoicesResponse
from ....chat.choices.services import static_check_is_chat_choices_service
from ....chat.choices.types import AiChoice
from ....chat.messages import AiMessage
from ....chat.messages import AnyAiMessage
from ....chat.messages import Message
from ....chat.messages import SystemMessage
from ....chat.messages import ToolUseMessage
from ....chat.messages import UserMessage
from ....chat.tools.types import Tool
from ....models.configs import ModelName
from ....standard import ApiKey
from ....tools.types import ToolUse
from .names import MODEL_NAMES
from .protocol import build_protocol_chat_messages
from .protocol import build_protocol_tool


##


# @omlish-manifest $.minichain.registries.manifests.RegistryManifest(
#     name='anthropic',
#     type='ChatChoicesService',
# )
@static_check_is_chat_choices_service
class AnthropicChatChoicesService:
    DEFAULT_MODEL_NAME: ta.ClassVar[ModelName] = ModelName(check.not_none(MODEL_NAMES.default))

    def __init__(
            self,
            *configs: ApiKey | ModelName,
            http_client: http.AsyncHttpClient | None = None,
    ) -> None:
        super().__init__()

        self._http_client = http_client

        with tv.consume(*configs) as cc:
            self._api_key = check.not_none(ApiKey.pop_secret(cc, env='ANTHROPIC_API_KEY'))
            self._model_name = cc.pop(self.DEFAULT_MODEL_NAME)

    @classmethod
    def _get_msg_content(cls, m: Message) -> str | None:
        if isinstance(m, AiMessage):
            return check.isinstance(m.c, str)

        elif isinstance(m, (UserMessage, SystemMessage)):
            return check.isinstance(m.c, str)

        else:
            raise TypeError(m)

    async def invoke(
            self,
            request: ChatChoicesRequest,
            *,
            max_tokens: int = 4096,  # FIXME: ChatOption
    ) -> ChatChoicesResponse:
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
        )

        raw_request = msh.marshal(a_req)

        raw_response = await http.async_request(
            'https://api.anthropic.com/v1/messages',
            headers={
                http.consts.HEADER_CONTENT_TYPE: http.consts.CONTENT_TYPE_JSON,
                b'x-api-key': self._api_key.reveal().encode('utf-8'),
                b'anthropic-version': b'2023-06-01',
            },
            data=json.dumps(raw_request).encode('utf-8'),
            client=self._http_client,
        )

        response = json.loads(check.not_none(raw_response.data).decode('utf-8'))

        out: list[AnyAiMessage] = []
        for c in response['content']:
            if c['type'] == 'text':
                out.append(AiMessage(
                    check.not_none(c['text']),
                ))
            elif c['type'] == 'tool_use':
                out.append(ToolUseMessage(ToolUse(
                    id=c['id'],
                    name=c['name'],
                    args=c['input'],
                )))
            else:
                raise TypeError(c['type'])

        return ChatChoicesResponse([
            AiChoice(out),
        ])
