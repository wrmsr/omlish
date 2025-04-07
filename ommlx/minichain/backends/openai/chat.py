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

from omlish import cached
from omlish import check
from omlish import lang
from omlish import typedvalues as tv
from omlish.formats import json
from omlish.http import all as http
from omlish.secrets.secrets import Secret

from ...chat.choices import AiChoice
from ...chat.messages import AiMessage
from ...chat.messages import Message
from ...chat.messages import SystemMessage
from ...chat.messages import ToolExecRequest
from ...chat.messages import ToolExecResultMessage
from ...chat.messages import UserMessage
from ...chat.services import ChatRequest
from ...chat.services import ChatResponse
from ...chat.services import ChatService
from ...chat.tools import Tool
from ...chat.tools import ToolSpec
from ...llms import MaxTokens
from ...llms import Temperature
from ...llms import TokenUsage
from ...llms import TokenUsageOutput
from ...services import RequestOption
from .format import build_request_message
from .format import render_tool_spec


##


class OpenaiChatRequestHandler:
    def __init__(
            self,
            *,
            request: ChatRequest,
            model: str,
    ) -> None:
        super().__init__()

        self._request = request
        self._model = model

    ROLES_MAP: ta.ClassVar[ta.Mapping[type[Message], str]] = {
        SystemMessage: 'system',
        UserMessage: 'user',
        AiMessage: 'assistant',
        ToolExecResultMessage: 'tool',
    }

    DEFAULT_OPTIONS: ta.ClassVar[tv.TypedValues[RequestOption]] = tv.TypedValues(
        Temperature(0.),
        MaxTokens(1024),
    )

    _OPTION_KWARG_NAMES_MAP: ta.Mapping[type[tv.ScalarTypedValue], str] = {
        Temperature: 'temperature',
        MaxTokens: 'max_tokens',
    }

    class _ProcessedOptions(ta.NamedTuple):
        kwargs: dict[str, ta.Any]
        tools_by_name: dict[str, ToolSpec]

    @cached.function
    def _process_options(self) -> _ProcessedOptions:
        kwargs: dict = dict(
            temperature=0,
            max_tokens=1024,
        )

        tools_by_name: dict[str, ToolSpec] = {}

        for opt in self._request.options:
            if (
                    isinstance(opt, tv.ScalarTypedValue) and
                    (kwn := self._OPTION_KWARG_NAMES_MAP.get(type(opt))) is not None
            ):
                kwargs[kwn] = opt.v

            elif isinstance(opt, Tool):
                if opt.spec.name in tools_by_name:
                    raise NameError(opt.spec.name)
                tools_by_name[opt.spec.name] = opt.spec

            else:
                raise TypeError(opt)

        return self._ProcessedOptions(
            kwargs=kwargs,
            tools_by_name=tools_by_name,
        )

    @cached.function
    def raw_request(self) -> ta.Mapping[str, ta.Any]:
        po = self._process_options()

        tools = [
            dict(
                type='function',
                function=render_tool_spec(ts),
            )
            for ts in po.tools_by_name.values()
        ]

        return dict(
            model=self._model,
            messages=[
                build_request_message(m)
                for m in self._request.chat
            ],
            top_p=1,
            **lang.opt_kw(tools=tools),
            frequency_penalty=0.0,
            presence_penalty=0.0,
            stream=False,
            **po.kwargs,
        )

    def build_response(self, raw_response: ta.Mapping[str, ta.Any]) -> ChatResponse:
        po = self._process_options()

        return ChatResponse(
            [
                AiChoice(AiMessage(
                    choice['message']['content'],
                    tool_exec_requests=[
                        ToolExecRequest(
                            id=tc['id'],
                            spec=po.tools_by_name[tc['function']['name']],
                            args=tc['function']['arguments'],
                        )
                        for tc in choice['message'].get('tool_calls', [])
                    ],
                ))
                for choice in raw_response['choices']
            ],

            outputs=tv.TypedValues(
                *([TokenUsageOutput(TokenUsage(
                    input=tu['prompt_tokens'],
                    output=tu['completion_tokens'],
                    total=tu['total_tokens'],
                ))] if (tu := raw_response.get('usage')) is not None else []),
            ),
        )


##


# @omlish-manifest ommlx.minichain.backends.manifests.BackendManifest(name='openai', type='ChatService')
class OpenaiChatService(
    ChatService[
        ChatRequest,
        ChatResponse,
    ],
    request=ChatRequest,
    response=ChatResponse,
):
    DEFAULT_MODEL: ta.ClassVar[str] = (
        'gpt-4o'
        # 'gpt-4o-mini'
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

    def invoke(self, request: ChatRequest) -> ChatResponse:
        check.isinstance(request, ChatRequest)

        rh = OpenaiChatRequestHandler(
            request=request,
            model=self._model,
        )

        raw_request = rh.raw_request()

        http_response = http.request(
            'https://api.openai.com/v1/chat/completions',
            headers={
                http.consts.HEADER_CONTENT_TYPE: http.consts.CONTENT_TYPE_JSON,
                http.consts.HEADER_AUTH: http.consts.format_bearer_auth_header(check.not_none(self._api_key).reveal()),
            },
            data=json.dumps(raw_request).encode('utf-8'),
        )

        raw_response = json.loads(check.not_none(http_response.data).decode('utf-8'))

        return rh.build_response(raw_response)
