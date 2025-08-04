import dataclasses as dc
import functools
import typing as ta

from omlish import check
from omlish import lang

from .... import minichain as mc
from ...state import StateStorage
from .base import CHAT_CHOICES_SERVICE_FACTORIES
from .base import DEFAULT_CHAT_MODEL_BACKEND
from .base import ChatSession
from .state import ChatState


if ta.TYPE_CHECKING:
    from omdev import ptk
else:
    ptk = lang.proxy_import('omdev.ptk')


##


class InteractiveChatSession(ChatSession['InteractiveChatSession.Config']):
    @dc.dataclass(frozen=True)
    class Config(ChatSession.Config):
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

        backend = self._config.backend
        if backend is None:
            backend = DEFAULT_CHAT_MODEL_BACKEND

        csf: ta.Callable[..., mc.ChatChoicesService]
        if (bf := CHAT_CHOICES_SERVICE_FACTORIES.get(backend)) is not None:
            csf = bf
        else:
            csf = functools.partial(mc.registry_of[mc.ChatChoicesService].new, backend)

        with lang.maybe_managing(csf(
                *([mc.ModelName(mn)] if (mn := self._config.model_name) is not None else []),
        )) as mdl:
            while True:
                prompt = ptk.prompt('> ')

                state = dc.replace(
                    state,
                    chat=[
                        *state.chat,
                        mc.UserMessage(prompt),
                    ],
                )

                response = mdl.invoke(mc.ChatChoicesRequest(state.chat))
                print(check.isinstance(response.v[0].m.c, str).strip())

                state = dc.replace(
                    state,
                    chat=[
                        *state.chat,
                        response.v[0].m,
                    ],
                    updated_at=lang.utcnow(),
                )

                self._state_storage.save_state('chat', state, ChatState)
