import dataclasses as dc

from omlish import lang

from .... import minichain as mc
from ....minichain.lib.code.prompts import CODE_AGENT_SYSTEM_PROMPT
from .base import DEFAULT_CHAT_MODEL_BACKEND
from .base import ChatOptions
from .base import ChatSession
from .printing import ChatSessionPrinter
from .state import ChatStateManager
from .tools import ToolExecRequestExecutor


with lang.auto_proxy_import(globals()):
    from omdev import ptk


##


class CodeChatSession(ChatSession['CodeChatSession.Config']):
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
            chat_options: ChatOptions | None = None,
            printer: ChatSessionPrinter,
            backend_catalog: mc.BackendCatalog,
            tool_exec_request_executor: ToolExecRequestExecutor,
    ) -> None:
        super().__init__(config)

        self._state_manager = state_manager
        self._chat_options = chat_options
        self._printer = printer
        self._backend_catalog = backend_catalog
        self._tool_exec_request_executor = tool_exec_request_executor

    async def run(self) -> None:
        if self._config.new:
            self._state_manager.clear_state()
            state = self._state_manager.extend_chat([
                mc.SystemMessage(CODE_AGENT_SYSTEM_PROMPT),
            ])

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
                prompt = await ptk.prompt('> ')

                req_msg = mc.UserMessage(prompt)

                response = await mdl.invoke(mc.ChatChoicesRequest(
                    [*state.chat, req_msg],
                    (self._chat_options or []),
                ))

                resp_msg = response.v[0].m

                self._printer.print(resp_msg)

                state = self._state_manager.extend_chat([req_msg, resp_msg])
