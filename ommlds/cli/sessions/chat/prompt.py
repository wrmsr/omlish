import dataclasses as dc
import os

from omlish import check
from omlish import lang

from .... import minichain as mc
from .base import DEFAULT_CHAT_MODEL_BACKEND
from .base import ChatOptions
from .base import ChatSession
from .printing import ChatSessionPrinter
from .state import ChatStateManager
from .tools import ToolUseExecutor


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
            tool_exec_request_executor: ToolUseExecutor,
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
        async with lang.async_maybe_managing(self._backend_catalog.get_backend(
            mc.ChatChoicesStreamService,
            self._config.backend or DEFAULT_CHAT_MODEL_BACKEND,
            *([mc.ModelName(mn)] if (mn := self._config.model_name) is not None else []),
        )) as mdl:
            async with (await mdl.invoke(mc.ChatChoicesStreamRequest(
                    [*state.chat, *new_chat],
                    (self._chat_options or []),
            ))).v as st_resp:
                lst: list[str] = []
                async for o in st_resp:
                    if o:
                        c = check.isinstance(check.single(check.single(o.choices).deltas), mc.ContentAiChoiceDelta).c
                        if c is not None:
                            print(check.isinstance(c, str), end='', flush=True)
                            lst.append(check.isinstance(c, str))
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
        async with lang.async_maybe_managing(self._backend_catalog.get_backend(
            mc.ChatChoicesService,
                self._config.backend or DEFAULT_CHAT_MODEL_BACKEND,
                *([mc.ModelName(mn)] if (mn := self._config.model_name) is not None else []),
        )) as mdl:
            response: mc.ChatChoicesResponse = await mdl.invoke(mc.ChatChoicesRequest(
                [*state.chat, *new_chat],
                (self._chat_options or []),
            ))

            for resp_m in response.v[0].ms:
                new_chat.append(resp_m)

                if isinstance(resp_m, mc.AiMessage):
                    self._printer.print(resp_m)

                elif isinstance(resp_m, mc.ToolUseMessage):
                    tr: mc.ToolUse = resp_m.tu

                    # FIXME: lol
                    from ....minichain.lib.fs.context import FsContext

                    trm = await self._tool_exec_request_executor.execute_tool_use(
                        tr,
                        FsContext(root_dir=os.getcwd()),
                    )

                    print(trm.tur.c)
                    new_chat.append(trm)

                    response = await mdl.invoke(mc.ChatChoicesRequest(
                        [*state.chat, *new_chat],
                        (self._chat_options or []),
                    ))

                    resp_m = check.isinstance(check.single(response.v[0].ms), mc.AiMessage)
                    new_chat.append(resp_m)

                else:
                    raise TypeError(resp_m)

        self._state_manager.extend_chat(new_chat)
