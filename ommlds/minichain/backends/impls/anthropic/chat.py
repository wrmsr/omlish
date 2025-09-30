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
from ....chat.messages import ToolUseResultMessage
from ....chat.messages import UserMessage
from ....chat.tools.types import Tool
from ....content.prepare import prepare_content_str
from ....models.configs import ModelName
from ....standard import ApiKey
from ....tools.jsonschema import build_tool_spec_params_json_schema
from ....tools.types import ToolUse
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
        ToolUseMessage: 'assistant',
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
        messages: list[pt.Message] = []
        system: list[pt.Content] | None = None
        for i, m in enumerate(request.v):
            if isinstance(m, SystemMessage):
                if i != 0 or system is not None:
                    raise Exception('Only supports one system message and must be first')
                system = [pt.Text(check.not_none(self._get_msg_content(m)))]

            elif isinstance(m, ToolUseResultMessage):
                messages.append(pt.Message(
                    role='user',
                    content=[pt.ToolResult(
                        tool_use_id=check.not_none(m.tur.id),
                        content=json.dumps_compact(msh.marshal(m.tur.c)) if not isinstance(m.tur.c, str) else m.tur.c,
                    )],
                ))

            elif isinstance(m, AiMessage):
                # messages.append(pt.Message(
                #     role=self.ROLES_MAP[type(m)],  # noqa
                #     content=[pt.Text(check.isinstance(self._get_msg_content(m), str))],
                # ))
                messages.append(pt.Message(
                    role='assistant',
                    content=[
                        *([pt.Text(check.isinstance(m.c, str))] if m.c is not None else []),
                    ],
                ))

            elif isinstance(m, ToolUseMessage):
                messages.append(pt.Message(
                    role='assistant',
                    content=[
                        pt.ToolUse(
                            id=check.not_none(m.tu.id),
                            name=check.not_none(m.tu.name),
                            input=m.tu.args,
                        ),
                    ],
                ))

            else:
                messages.append(pt.Message(
                    role=self.ROLES_MAP[type(m)],  # type: ignore[arg-type]
                    content=[pt.Text(check.isinstance(self._get_msg_content(m), str))],
                ))

        tools: list[pt.ToolSpec] = []
        with tv.TypedValues(*request.options).consume() as oc:
            t: Tool
            for t in oc.pop(Tool, []):
                tools.append(pt.ToolSpec(
                    name=check.not_none(t.spec.name),
                    description=prepare_content_str(t.spec.desc),
                    input_schema=build_tool_spec_params_json_schema(t.spec),
                ))

        a_req = pt.MessagesRequest(
            model=MODEL_NAMES.resolve(self._model_name.v),
            system=system,
            messages=messages,
            tools=tools or None,
            max_tokens=max_tokens,
        )

        raw_request = msh.marshal(a_req)

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
