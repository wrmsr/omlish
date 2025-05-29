import dataclasses as dc
import datetime
import typing as ta

from omlish import check
from omlish import lang
from omlish import marshal as msh
from omlish.formats import json

from ... import minichain as mc
from ..state import StateStorage
from ..tools.tools import ToolMap
from .base import Session


if ta.TYPE_CHECKING:
    from omdev import ptk
    from omdev.ptk import markdown as ptk_md

    from ...minichain.backends import mistral as mc_mistral
    from ...minichain.backends.anthropic import chat as mc_anthropic
    from ...minichain.backends.google import chat as mc_google
    from ...minichain.backends.llamacpp import chat as mc_lcc
    from ...minichain.backends.mlx import chat as mc_mlx
    from ...minichain.backends.openai import chat as mc_openai

else:
    ptk = lang.proxy_import('omdev.ptk')
    ptk_md = lang.proxy_import('omdev.ptk.markdown')

    mc_mistral = lang.proxy_import('...minichain.backends.mistral', __package__)
    mc_anthropic = lang.proxy_import('...minichain.backends.anthropic.chat', __package__)
    mc_google = lang.proxy_import('...minichain.backends.google.chat', __package__)
    mc_lcc = lang.proxy_import('...minichain.backends.llamacpp.chat', __package__)
    mc_mlx = lang.proxy_import('...minichain.backends.mlx.chat', __package__)
    mc_openai = lang.proxy_import('...minichain.backends.openai.chat', __package__)


##


@dc.dataclass(frozen=True)
class ChatState:
    name: str | None = None

    created_at: datetime.datetime = dc.field(default_factory=lang.utcnow)
    updated_at: datetime.datetime = dc.field(default_factory=lang.utcnow)

    chat: mc.Chat = ()


##


DEFAULT_CHAT_MODEL_BACKEND = 'openai'

CHAT_MODEL_BACKENDS: ta.Mapping[str, ta.Callable[[], type[mc.ChatService]]] = {
    'anthropic': lambda: mc_anthropic.AnthropicChatService,
    'google': lambda: mc_google.GoogleChatService,
    'llamacpp': lambda: mc_lcc.LlamacppChatService,
    'mistral': lambda: mc_mistral.MistralChatService,
    'mlx': lambda: mc_mlx.MlxChatService,
    'openai': lambda: mc_openai.OpenaiChatService,
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
            with lang.maybe_managing(mc.backend_of[mc.ChatStreamService].new('openai')) as st_mdl:
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
            with lang.maybe_managing(CHAT_MODEL_BACKENDS[self._config.backend or DEFAULT_CHAT_MODEL_BACKEND]()(
                *([mc.ModelName(mn)] if (mn := self._config.model_name) is not None else []),
            )) as mdl:
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

            mdl = CHAT_MODEL_BACKENDS[self._config.backend or DEFAULT_CHAT_MODEL_BACKEND]()(
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
