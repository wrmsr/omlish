import dataclasses as dc
import itertools
import os.path

from omlish import check
from omlish import lang

from .... import minichain as mc
from ....minichain.lib.code.prompts import CODE_AGENT_SYSTEM_PROMPT
from ...tools.config import ToolsConfig
from .base import DEFAULT_CHAT_MODEL_BACKEND
from .base import ChatOptions
from .base import ChatSession
from .printing import ChatSessionPrinter
from .state import ChatStateManager
from .tools import ToolUseExecutor


##


class CodeChatSession(ChatSession['CodeChatSession.Config']):
    @dc.dataclass(frozen=True)
    class Config(ChatSession.Config):
        _: dc.KW_ONLY

        new: bool = False

        backend: str | None = None
        model_name: str | None = None

        initial_message: mc.Content | None = None

    def __init__(
            self,
            config: Config,
            *,
            state_manager: ChatStateManager,
            chat_options: ChatOptions | None = None,
            printer: ChatSessionPrinter,
            backend_catalog: mc.BackendCatalog,
            tool_exec_request_executor: ToolUseExecutor,
            tools_config: ToolsConfig | None = None,
    ) -> None:
        super().__init__(config)

        self._state_manager = state_manager
        self._chat_options = chat_options
        self._printer = printer
        self._backend_catalog = backend_catalog
        self._tool_exec_request_executor = tool_exec_request_executor
        self._tools_config = tools_config

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

        # FIXME: lol
        from ....minichain.lib.fs.context import FsContext
        fs_tool_context = FsContext(
            root_dir=os.getcwd(),
            writes_permitted=self._tools_config is not None and self._tools_config.enable_unsafe_tools_do_not_use_lol,
        )

        from ....minichain.lib.todo.context import TodoContext
        todo_tool_context = TodoContext()

        mdl: mc.ChatChoicesService
        async with lang.async_maybe_managing(self._backend_catalog.get_backend(
                mc.ChatChoicesService,
                backend,
                *([mc.ModelName(mn)] if (mn := self._config.model_name) is not None else []),
        )) as mdl:
            for i in itertools.count():
                if not i and self._config.initial_message is not None:
                    req_msg = mc.UserMessage(self._config.initial_message)
                else:
                    try:
                        prompt = input('> ')  # FIXME: async lol
                    except EOFError:
                        break
                    req_msg = mc.UserMessage(prompt)

                state = self._state_manager.extend_chat([req_msg])

                while True:
                    response = await mdl.invoke(mc.ChatChoicesRequest(
                        state.chat,
                        (self._chat_options or []),
                    ))

                    tool_resp_lst = []
                    for resp_msg in check.single(response.v).ms:
                        state = self._state_manager.extend_chat([resp_msg])

                        if isinstance(resp_msg, mc.AiMessage):
                            self._printer.print(resp_msg)

                        elif isinstance(resp_msg, mc.ToolUseMessage):
                            trm = await self._tool_exec_request_executor.execute_tool_use(
                                resp_msg.tu,
                                fs_tool_context,
                                todo_tool_context,
                            )

                            self._printer.print(trm.tur.c)
                            tool_resp_lst.append(trm)

                        else:
                            raise TypeError(resp_msg)

                    if not tool_resp_lst:
                        break

                    state = self._state_manager.extend_chat(tool_resp_lst)
