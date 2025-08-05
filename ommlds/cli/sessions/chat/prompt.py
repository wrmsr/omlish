import dataclasses as dc
import functools
import typing as ta

from omlish import check
from omlish import lang
from omlish import marshal as msh
from omlish.formats import json

from .... import minichain as mc
from .base import CHAT_CHOICES_SERVICE_FACTORIES
from .base import DEFAULT_CHAT_MODEL_BACKEND
from .base import ChatOptions
from .base import ChatSession
from .printing import ChatSessionPrinter
from .state import ChatStateManager


if ta.TYPE_CHECKING:
    from omdev import ptk
    from omdev.ptk import markdown as ptk_md
else:
    ptk = lang.proxy_import('omdev.ptk')
    ptk_md = lang.proxy_import('omdev.ptk.markdown')


##


class ToolExecutionRequestDeniedError(Exception):
    pass


class PromptChatSession(ChatSession['PromptChatSession.Config']):
    @dc.dataclass(frozen=True)
    class Config(ChatSession.Config):
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
            state_manager: ChatStateManager,
            chat_options: ChatOptions | None = None,
            tool_catalog: mc.ToolCatalog | None = None,
            printer: ChatSessionPrinter,
    ) -> None:
        super().__init__(config)

        self._state_manager = state_manager
        self._chat_options = chat_options
        self._tool_catalog = tool_catalog
        self._printer = printer

    def run(self) -> None:
        if self._config.stream:
            self._run_stream()
        else:
            self._run_immediate()

    def _run_stream(self) -> None:
        prompt = check.isinstance(self._config.content, str)

        if self._config.new:
            state = self._state_manager.clear_state()
        else:
            state = self._state_manager.get_state()

        backend = self._config.backend
        if backend is None:
            backend = DEFAULT_CHAT_MODEL_BACKEND

        new_chat: list[mc.Message] = [
            mc.UserMessage(prompt),
        ]

        with lang.maybe_managing(mc.registry_of[mc.ChatChoicesStreamService].new(backend)) as st_mdl:
            with st_mdl.invoke(mc.ChatChoicesStreamRequest(
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

    def _run_immediate(self) -> None:
        prompt = check.isinstance(self._config.content, str)

        if self._config.new:
            state = self._state_manager.clear_state()
        else:
            state = self._state_manager.get_state()

        backend = self._config.backend
        if backend is None:
            backend = DEFAULT_CHAT_MODEL_BACKEND

        new_chat: list[mc.Message] = [
            mc.UserMessage(prompt),
        ]

        csf: ta.Callable[..., mc.ChatChoicesService]
        if (bf := CHAT_CHOICES_SERVICE_FACTORIES.get(backend)) is not None:
            csf = bf
        else:
            csf = functools.partial(mc.registry_of[mc.ChatChoicesService].new, backend)

        with lang.maybe_managing(csf(
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
                tce = check.not_none(self._tool_catalog).by_name[check.non_empty_str(tr.name)]

                tr_dct = dict(
                    id=tr.id,
                    spec=msh.marshal(tce.spec),
                    args=tr.args,
                )
                cr = ptk.strict_confirm(f'Execute requested tool?\n\n{json.dumps_pretty(tr_dct)}\n\n')

                if not cr:
                    raise ToolExecutionRequestDeniedError

                trm = mc.execute_tool_request(
                    mc.ToolContext(),
                    check.not_none(self._tool_catalog),
                    tr,
                )
                new_chat.append(trm)

                response = mdl.invoke(mc.ChatChoicesRequest(
                    [*state.chat, *new_chat],
                    (self._chat_options or []),
                ))

                resp_m = response.v[0].m
                new_chat.append(resp_m)

            if self._config.markdown:
                ptk.print_formatted_text(
                    ptk_md.Markdown(check.isinstance(resp_m.c, str).strip()),
                    style=ptk.Style(list(ptk_md.MARKDOWN_STYLE)),
                )

            else:
                self._printer.print(resp_m)

        self._state_manager.extend_chat(new_chat)
