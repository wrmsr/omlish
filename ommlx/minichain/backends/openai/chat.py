"""
TODO:
 - defaults:
   {
     "frequency_penalty": 0.0,
     "max_tokens": 64,
     "messages": ...,
     "model": "gpt-4o",
     "presence_penalty": 0.0,
     "temperature": 0.1,
     "top_p": 1
   }
"""
import os
import typing as ta

from omlish import check
from omlish.formats import json
from omlish.http import all as http
from omlish.secrets.secrets import Secret

from ...chat.messages import AiMessage
from ...chat.messages import Message
from ...chat.messages import SystemMessage
from ...chat.messages import ToolExecRequest
from ...chat.messages import ToolExecResultMessage
from ...chat.messages import UserMessage
from ...chat.models import AiChoice
from ...chat.models import ChatModel
from ...chat.models import ChatRequest
from ...chat.models import ChatResponse
from ...chat.options import ChatOptions
from ...chat.tools import Tool
from ...chat.tools import ToolSpec
from ...generative import MaxTokens
from ...generative import Temperature
from ...models import TokenUsage
from ...options import Options
from ...options import ScalarOption


def _opt_dct_fld(k, v):
    return {k: v} if v else {}


def render_tool_spec(ts: ToolSpec) -> ta.Mapping[str, ta.Any]:
    return dict(
        name=ts.name,

        **_opt_dct_fld('description', ts.desc),

        parameters=dict(
            type='object',
            properties={
                tp.name: {
                    'type': tp.dtype,
                    **_opt_dct_fld('description', tp.desc),
                }
                for tp in ts.params
            },

            required=[tp.name for tp in ts.params if tp.required],
            additionalProperties=False,
        ),
    )


def build_request_message(m: Message) -> ta.Mapping[str, ta.Any]:
    if isinstance(m, SystemMessage):
        return dict(
            role='system',
            content=m.s,
        )

    elif isinstance(m, AiMessage):
        return dict(
            role='assistant',
            content=m.s,
            **(dict(tool_calls=[
                dict(
                    id=te.id,
                    function=dict(
                        arguments=te.args,
                        name=te.spec.name,
                    ),
                    type='function',
                )
                for te in m.tool_exec_requests
            ]) if m.tool_exec_requests else {}),
        )

    elif isinstance(m, UserMessage):
        return dict(
            role='user',
            content=check.isinstance(m.c, str),
        )

    elif isinstance(m, ToolExecResultMessage):
        return dict(
            role='tool',
            tool_call_id=m.id,
            content=m.s,
        )

    else:
        raise TypeError(m)


class OpenaiChatModel(ChatModel):
    DEFAULT_MODEL: ta.ClassVar[str] = (
        # 'gpt-4o'
        'gpt-4o-mini'
    )

    ROLES_MAP: ta.ClassVar[ta.Mapping[type[Message], str]] = {
        SystemMessage: 'system',
        UserMessage: 'user',
        AiMessage: 'assistant',
        ToolExecResultMessage: 'tool',
    }

    DEFAULT_OPTIONS: ta.ClassVar[Options[ChatOptions]] = Options(
        Temperature(0.),
        MaxTokens(1024),
    )

    def __init__(
            self,
            *,
            model: str | None = None,
            api_key: Secret | str | None = None,
    ) -> None:
        super().__init__()
        self._model = model or self.DEFAULT_MODEL
        self._api_key = Secret.of(api_key if api_key is not None else os.environ['OPENAI_API_KEY'])

    _OPTION_KWARG_NAMES_MAP: ta.Mapping[type[ScalarOption], str] = {
        Temperature: 'temperature',
        MaxTokens: 'max_tokens',
    }

    def invoke(self, request: ChatRequest) -> ChatResponse:
        kw: dict = dict(
            temperature=0,
            max_tokens=1024,
        )

        tools_by_name: dict[str, ToolSpec] = {}

        for opt in request.options:
            if isinstance(opt, ScalarOption) and (kwn := self._OPTION_KWARG_NAMES_MAP.get(type(opt))) is not None:
                kw[kwn] = opt.v

            elif isinstance(opt, Tool):
                if opt.spec.name in tools_by_name:
                    raise NameError(opt.spec.name)
                tools_by_name[opt.spec.name] = opt.spec

            else:
                raise TypeError(opt)

        tools = [
            dict(
                type='function',
                function=render_tool_spec(ts),
            )
            for ts in tools_by_name.values()
        ]

        raw_request = dict(
            model=self._model,
            messages=[
                build_request_message(m)
                for m in request.v
            ],
            top_p=1,
            **(dict(tools=tools) if tools else {}),
            frequency_penalty=0.0,
            presence_penalty=0.0,
            stream=False,
            **kw,
        )

        raw_response = http.request(
            'https://api.openai.com/v1/chat/completions',
            headers={
                http.consts.HEADER_CONTENT_TYPE: http.consts.CONTENT_TYPE_JSON,
                http.consts.HEADER_AUTH: http.consts.format_bearer_auth_header(check.not_none(self._api_key).reveal()),
            },
            data=json.dumps(raw_request).encode('utf-8'),
        )

        response = json.loads(check.not_none(raw_response.data).decode('utf-8'))

        return ChatResponse(
            v=[
                AiChoice(AiMessage(
                    choice['message']['content'],
                    tool_exec_requests=[
                        ToolExecRequest(
                            id=tc['id'],
                            spec=tools_by_name[tc['function']['name']],
                            args=tc['function']['arguments'],
                        )
                        for tc in choice['message'].get('tool_calls', [])
                    ],
                ))
                for choice in response['choices']
            ],
            usage=TokenUsage(
                input=response['usage']['prompt_tokens'],
                output=response['usage']['completion_tokens'],
                total=response['usage']['total_tokens'],
            ) if response.get('usage') is not None else None,
        )
