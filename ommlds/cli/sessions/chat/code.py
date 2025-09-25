import dataclasses as dc
import itertools
import os.path

from omlish import check
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

        initial_message: mc.Content | None = None

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

        # FIXME: lol
        from ....minichain.lib.fs.context import FsToolContext
        fs_tool_context = FsToolContext(root_dir=os.getcwd())
        from ....minichain.lib.todo.context import TodoToolContext
        todo_tool_context = TodoToolContext()

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
                    prompt = await ptk.prompt('> ')
                    req_msg = mc.UserMessage(prompt)

                state = self._state_manager.extend_chat([req_msg])

                while True:
                    response = await mdl.invoke(mc.ChatChoicesRequest(
                        state.chat,
                        (self._chat_options or []),
                    ))
                    resp_msg = check.single(response.v).m

                    self._printer.print(resp_msg)
                    state = self._state_manager.extend_chat([resp_msg])

                    if not (trs := resp_msg.tool_exec_requests):
                        break

                    tool_resp_lst = []
                    for tr in trs:
                        trm = await self._tool_exec_request_executor.execute_tool_request(
                            tr,
                            fs_tool_context,
                            todo_tool_context,
                        )

                        self._printer.print(trm.c)
                        tool_resp_lst.append(trm)

                    state = self._state_manager.extend_chat(tool_resp_lst)
