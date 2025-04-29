import dataclasses as dc
import datetime
import typing as ta

from omlish import check
from omlish import lang

from ... import minichain as mc
from ...minichain.backends.anthropic.chat import AnthropicChatService
from ...minichain.backends.google.chat import GoogleChatService
from ...minichain.backends.llamacpp.chat import LlamacppChatService
from ...minichain.backends.mistral import MistralChatService
from ...minichain.backends.mlx import MlxChatService
from ...minichain.backends.openai.chat import OpenaiChatService
from ..state import StateStorage
from .base import Session


if ta.TYPE_CHECKING:
    from omdev import ptk

else:
    ptk = lang.proxy_import('omdev.ptk')


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


class PromptChatSession(Session['PromptChatSession.Config']):
    @dc.dataclass(frozen=True)
    class Config(Session.Config):
        content: mc.Content

        _: dc.KW_ONLY

        new: bool = False
        backend: str | None = None
        model_name: str | None = None
        stream: bool = False

    def __init__(
            self,
            config: Config,
            *,
            state_storage: StateStorage,
    ) -> None:
        super().__init__(config)

        self._state_storage = state_storage

    def run(self) -> None:
        prompt = check.isinstance(self._config.content, str)

        if self._config.new:
            state = ChatState()
        else:
            state = self._state_storage.load_state('chat', ChatState)  # type: ignore
            if state is None:
                state = ChatState()  # type: ignore

        state = dc.replace(
            state,
            chat=[
                *state.chat,
                mc.UserMessage(prompt),
            ],
        )

        if self._config.stream:
            st_mdl = mc.backend_of[mc.ChatStreamService].new('openai')
            with st_mdl.invoke(mc.ChatStreamRequest(state.chat)) as st_resp:
                resp_s = ''
                for o in st_resp:
                    o_s = check.isinstance(o[0].m.s, str)
                    print(o_s, end='', flush=True)
                    resp_s += o_s
                print()
            resp_m = mc.AiMessage(resp_s)

        else:
            mdl = CHAT_MODEL_BACKENDS[self._config.backend or DEFAULT_CHAT_MODEL_BACKEND](
                *([mc.ModelName(mn)] if (mn := self._config.model_name) is not None else []),
            )

            response = mdl.invoke(mc.ChatRequest.new(state.chat))
            resp_m = response.choices[0].m
            print(check.isinstance(resp_m.s, str).strip())

        state = dc.replace(
            state,
            chat=[
                *state.chat,
                resp_m,
            ],
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
