import dataclasses as dc
import datetime
import typing as ta

from omlish import check
from omlish import lang
from omlish import marshal as msh
from omlish.formats import json

from ... import minichain as mc
from ...minichain.backends.anthropic.chat import AnthropicChatService
from ...minichain.backends.google.chat import GoogleChatService
from ...minichain.backends.llamacpp.chat import LlamacppChatService
from ...minichain.backends.mistral import MistralChatService
from ...minichain.backends.mlx import MlxChatService
from ...minichain.backends.openai.chat import OpenaiChatService
from ..state import StateStorage
from ..tools.tools import ToolMap
from .base import Session


if ta.TYPE_CHECKING:
    from omdev import ptk
    from omdev.ptk import markdown as ptk_md

else:
    ptk = lang.proxy_import('omdev.ptk')
    ptk_md = lang.proxy_import('omdev.ptk.markdown')


##


@dc.dataclass(frozen=True)
class ChatState:
    name: str | None = None

    created_at: datetime.datetime = dc.field(default_factory=lang.utcnow)
    updated_at: datetime.datetime = dc.field(default_factory=lang.utcnow)

    chat: mc.Chat = ()


##


DEFAULT_CHAT_MODEL_BACKEND = 'openai'

CHAT_MODEL_BACKENDS: ta.Mapping[str, type[mc.ChatService]] = {
    'anthropic': AnthropicChatService,
    'google': GoogleChatService,
    'llamacpp': LlamacppChatService,
    'mistral': MistralChatService,
    'mlx': MlxChatService,
    'openai': OpenaiChatService,
}


##


ChatOption: ta.TypeAlias = mc.ChatRequestOption | mc.LlmRequestOption
ChatOptions = ta.NewType('ChatOptions', ta.Sequence[ChatOption])


class ToolExecutionRequestDeniedError(Exception):
    pass


class PromptChatSession(Session['PromptChatSession.Config']):
    @dc.dataclass(frozen=True)
    class Config(Session.Config):
        content: mc.Content

        _: dc.KW_ONLY

        new: bool = False
        backend: str | None = None
        model_name: str | None = None
        stream: bool = False
        markdown: bool = False

    def __init__(
            self,
            config: Config,
            *,
            state_storage: StateStorage,
            chat_options: ChatOptions | None = None,
            tool_map: ToolMap | None = None,
    ) -> None:
        super().__init__(config)

        self._state_storage = state_storage
        self._chat_options = chat_options
        self._tool_map = tool_map

    def run(self) -> None:
        prompt = check.isinstance(self._config.content, str)

        if self._config.new:
            state = ChatState()
        else:
            state = self._state_storage.load_state('chat', ChatState)  # type: ignore
            if state is None:
                state = ChatState()  # type: ignore

        chat: list[mc.Message] = [
            *state.chat,
            mc.UserMessage(prompt),
        ]

        if self._config.stream:
            st_mdl = mc.backend_of[mc.ChatStreamService].new('openai')
            with st_mdl.invoke(mc.ChatStreamRequest.new(
                    chat,
                    *(self._chat_options or []),
            )) as st_resp:
                resp_s = ''
                for o in st_resp:
                    o_s = check.isinstance(o[0].m.s, str)
                    print(o_s, end='', flush=True)
                    resp_s += o_s
                print()

            resp_m = mc.AiMessage(resp_s)
            chat.append(resp_m)

        else:
            mdl = CHAT_MODEL_BACKENDS[self._config.backend or DEFAULT_CHAT_MODEL_BACKEND](
                *([mc.ModelName(mn)] if (mn := self._config.model_name) is not None else []),
            )

            response = mdl.invoke(mc.ChatRequest.new(
                chat,
                *(self._chat_options or []),
            ))

            resp_m = response.choices[0].m
            chat.append(resp_m)

            if (trs := resp_m.tool_exec_requests):
                check.state(resp_m.s is None)

                tr: mc.ToolExecRequest = check.single(check.not_none(trs))
                tool = check.not_none(self._tool_map)[tr.spec.name]

                tr_dct = dict(
                    id=tr.id,
                    spec=msh.marshal(tr.spec),
                    args=tr.args,
                )
                cr = ptk.strict_confirm(f'Execute requested tool?\n\n{json.dumps_pretty(tr_dct)}\n\n')

                if not cr:
                    raise ToolExecutionRequestDeniedError

                tool_res = tool.fn(**tr.args)
                chat.append(mc.ToolExecResultMessage(tr.id, tr.spec.name, json.dumps(tool_res)))

                response = mdl.invoke(mc.ChatRequest.new(
                    chat,
                    *(self._chat_options or []),
                ))

                resp_m = response.choices[0].m
                chat.append(resp_m)

            resp_s = check.isinstance(resp_m.s, str).strip()

            if self._config.markdown:
                ptk.print_formatted_text(
                    ptk_md.Markdown(resp_s),
                    style=ptk.Style(list(ptk_md.MARKDOWN_STYLE)),
                )

            else:
                print(resp_s)

        state = dc.replace(
            state,
            chat=tuple(chat),
            updated_at=lang.utcnow(),
        )

        self._state_storage.save_state('chat', state, ChatState)


##


class InteractiveChatSession(Session['InteractiveChatSession.Config']):
    @dc.dataclass(frozen=True)
    class Config(Session.Config):
        _: dc.KW_ONLY

        new: bool = False
        backend: str | None = None
        model_name: str | None = None

    def __init__(
            self,
            config: Config,
            *,
            state_storage: StateStorage,
    ) -> None:
        super().__init__(config)

        self._state_storage = state_storage

    def run(self) -> None:
        if self._config.new:
            state = ChatState()
        else:
            state = self._state_storage.load_state('chat', ChatState)  # type: ignore
            if state is None:
                state = ChatState()  # type: ignore

        while True:
            prompt = ptk.prompt('> ')

            state = dc.replace(
                state,
                chat=[
                    *state.chat,
                    mc.UserMessage(prompt),
                ],
            )

            mdl = CHAT_MODEL_BACKENDS[self._config.backend or DEFAULT_CHAT_MODEL_BACKEND](
                *([mc.ModelName(mn)] if (mn := self._config.model_name) is not None else []),
            )

            response = mdl.invoke(mc.ChatRequest.new(state.chat))
            print(check.isinstance(response.choices[0].m.s, str).strip())

            state = dc.replace(
                state,
                chat=[
                    *state.chat,
                    response.choices[0].m,
                ],
                updated_at=lang.utcnow(),
            )

            self._state_storage.save_state('chat', state, ChatState)
