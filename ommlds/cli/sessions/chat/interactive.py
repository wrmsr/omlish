import dataclasses as dc

from omlish import check
from omlish import lang

from .... import minichain as mc
from .base import DEFAULT_CHAT_MODEL_BACKEND
from .base import ChatSession
from .printing import ChatSessionPrinter
from .state import ChatStateManager


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
            state_manager: ChatStateManager,
            printer: ChatSessionPrinter,
            backend_catalog: mc.BackendCatalog,
    ) -> None:
        super().__init__(config)

        self._state_manager = state_manager
        self._printer = printer
        self._backend_catalog = backend_catalog

    async def run(self) -> None:
        if self._config.new:
            state = self._state_manager.clear_state()
        else:
            state = self._state_manager.get_state()

        backend = self._config.backend
        if backend is None:
            backend = DEFAULT_CHAT_MODEL_BACKEND

        mdl: mc.ChatChoicesService
        async with lang.async_maybe_managing(self._backend_catalog.get_backend(
                mc.ChatChoicesService,
                backend,
                *([mc.ModelName(mn)] if (mn := self._config.model_name) is not None else []),
        )) as mdl:
            while True:
                try:
                    prompt = input('> ')  # FIXME: async lol
                except EOFError:
                    break

                req_msg = mc.UserMessage(prompt)

                response = await mdl.invoke(mc.ChatChoicesRequest([*state.chat, req_msg]))

                resp_msg = check.isinstance(check.single(response.v[0].ms), mc.AiMessage)

                self._printer.print(resp_msg)

                state = self._state_manager.extend_chat([req_msg, resp_msg])
