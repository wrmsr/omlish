"""
https://docs.claude.com/en/api/messages
https://github.com/anthropics/anthropic-sdk-python/tree/cd80d46f7a223a5493565d155da31b898a4c6ee5/src/anthropic/types
https://github.com/anthropics/anthropic-sdk-python/blob/cd80d46f7a223a5493565d155da31b898a4c6ee5/src/anthropic/resources/completions.py#L53
https://github.com/anthropics/anthropic-sdk-python/blob/cd80d46f7a223a5493565d155da31b898a4c6ee5/src/anthropic/resources/messages.py#L70
"""
import typing as ta

from omlish import check
from omlish import lang
from omlish import typedvalues as tv
from omlish.formats import json
from omlish.http import all as http

from ....chat.choices.services import ChatChoicesRequest
from ....chat.choices.services import ChatChoicesResponse
from ....chat.choices.services import static_check_is_chat_choices_service
from ....chat.choices.types import AiChoice
from ....chat.messages import AiMessage
from ....chat.messages import Message
from ....chat.messages import SystemMessage
from ....chat.messages import ToolExecResultMessage
from ....chat.messages import UserMessage
from ....chat.tools.types import Tool
from ....models.configs import ModelName
from ....standard import ApiKey
from ....tools.jsonschema import build_tool_spec_params_json_schema
from ....tools.types import ToolExecRequest
from .names import MODEL_NAMES


##


# @omlish-manifest $.minichain.registries.manifests.RegistryManifest(
#     name='anthropic',
#     type='ChatChoicesService',
# )
@static_check_is_chat_choices_service
class AnthropicChatChoicesService:
    DEFAULT_MODEL_NAME: ta.ClassVar[ModelName] = ModelName(check.not_none(MODEL_NAMES.default))

    ROLES_MAP: ta.ClassVar[ta.Mapping[type[Message], str]] = {
        SystemMessage: 'system',
        UserMessage: 'user',
        AiMessage: 'assistant',
    }

    def __init__(
            self,
            *configs: ApiKey | ModelName,
    ) -> None:
        super().__init__()

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
        messages = []
        system: str | None = None
        for i, m in enumerate(request.v):
            if isinstance(m, SystemMessage):
                if i != 0 or system is not None:
                    raise Exception('Only supports one system message and must be first')
                system = self._get_msg_content(m)
            elif isinstance(m, ToolExecResultMessage):
                messages.append(dict(
                    role='user',
                    content=dict(
                        tool_use_id=m.id,
                        type='tool_result',
                        content=m.c,
                    ),
                ))
            else:
                messages.append(dict(
                    role=self.ROLES_MAP[type(m)],  # noqa
                    content=check.isinstance(self._get_msg_content(m), str),
                ))

        tools: list[dict[str, ta.Any]] = []
        with tv.TypedValues(*request.options).consume() as oc:
            t: Tool
            for t in oc.pop(Tool, []):
                tools.append(dict(
                    name=check.not_none(t.spec.name),
                    description=t.spec.desc,
                    input_schema=build_tool_spec_params_json_schema(t.spec),
                ))

        raw_request = dict(
            model=MODEL_NAMES.resolve(self._model_name.v),
            **lang.opt_kw(system=system),
            **(dict(tools=tools) if tools else {}),
            messages=messages,
            max_tokens=max_tokens,
        )

        raw_response = http.request(
            'https://api.anthropic.com/v1/messages',
            headers={
                http.consts.HEADER_CONTENT_TYPE: http.consts.CONTENT_TYPE_JSON,
                b'x-api-key': self._api_key.reveal().encode('utf-8'),
                b'anthropic-version': b'2023-06-01',
            },
            data=json.dumps(raw_request).encode('utf-8'),
        )

        response = json.loads(check.not_none(raw_response.data).decode('utf-8'))

        resp_c: ta.Any = None
        ters: list[ToolExecRequest] = []
        for c in response['content']:
            if c['type'] == 'text':
                check.none(resp_c)
                resp_c = check.not_none(c['text'])
            elif c['type'] == 'tool_use':
                ters.append(ToolExecRequest(
                    id=c['id'],
                    name=c['name'],
                    args=c['input'],
                ))
            else:
                raise TypeError(c['type'])

        return ChatChoicesResponse([
            AiChoice(AiMessage(
                resp_c,
                tool_exec_requests=ters if ters else None,
            )),
        ])
