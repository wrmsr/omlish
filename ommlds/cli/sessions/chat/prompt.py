import dataclasses as dc

from omlish import check
from omlish import lang

from .... import minichain as mc
from .base import DEFAULT_CHAT_MODEL_BACKEND
from .base import ChatOptions
from .base import ChatSession
from .printing import ChatSessionPrinter
from .state import ChatStateManager
from .tools import ToolExecRequestExecutor


##


class ToolExecutionRequestDeniedError(Exception):
    pass


class PromptChatSession(ChatSession['PromptChatSession.Config']):
    @dc.dataclass(frozen=True)
    class Config(ChatSession.Config):  # noqa
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
        if self._config.stream:
            await self._run_stream()
        else:
            await self._run_immediate()

    async def _run_stream(self) -> None:
        prompt = check.isinstance(self._config.content, str)

        if self._config.new:
            state = self._state_manager.clear_state()
        else:
            state = self._state_manager.get_state()

        new_chat: list[mc.Message] = [
            mc.UserMessage(prompt),
        ]

        mdl: mc.ChatChoicesStreamService
        with lang.maybe_managing(self._backend_catalog.get_backend(
            mc.ChatChoicesStreamService,
            self._config.backend or DEFAULT_CHAT_MODEL_BACKEND,
            *([mc.ModelName(mn)] if (mn := self._config.model_name) is not None else []),
        )) as mdl:
            with mdl.invoke(mc.ChatChoicesStreamRequest(
                    [*state.chat, *new_chat],
                    (self._chat_options or []),
            )).v as st_resp:
                lst: list[str] = []
                for o in st_resp:
                    if o:
                        m = check.single(o).m
                        if m.c is not None:
                            print(check.isinstance(m.c, str), end='', flush=True)
                            lst.append(check.isinstance(m.c, str))
                        check.none(m.tool_exec_requests)
                print()

            resp_m = mc.AiMessage(''.join(lst))
            new_chat.append(resp_m)

        self._state_manager.extend_chat(new_chat)

    async def _run_immediate(self) -> None:
        prompt = check.isinstance(self._config.content, str)

        if self._config.new:
            state = self._state_manager.clear_state()
        else:
            state = self._state_manager.get_state()

        new_chat: list[mc.Message] = [
            mc.UserMessage(prompt),
        ]

        mdl: mc.ChatChoicesService
        with lang.maybe_managing(self._backend_catalog.get_backend(
            mc.ChatChoicesService,
                self._config.backend or DEFAULT_CHAT_MODEL_BACKEND,
                *([mc.ModelName(mn)] if (mn := self._config.model_name) is not None else []),
        )) as mdl:
            response: mc.ChatChoicesResponse = mdl.invoke(mc.ChatChoicesRequest(
                [*state.chat, *new_chat],
                (self._chat_options or []),
            ))

            resp_m = response.v[0].m
            new_chat.append(resp_m)

            if (trs := resp_m.tool_exec_requests):
                check.state(resp_m.c is None)

                tr: mc.ToolExecRequest = check.single(check.not_none(trs))

                trm = await self._tool_exec_request_executor.execute_tool_request(tr)

                print(trm.c)
                new_chat.append(trm)

                response = mdl.invoke(mc.ChatChoicesRequest(
                    [*state.chat, *new_chat],
                    (self._chat_options or []),
                ))

                resp_m = response.v[0].m
                new_chat.append(resp_m)

            self._printer.print(resp_m)

        self._state_manager.extend_chat(new_chat)
