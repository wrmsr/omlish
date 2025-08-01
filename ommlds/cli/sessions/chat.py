import dataclasses as dc
import datetime
import functools
import typing as ta

from omlish import check
from omlish import collections as col
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

else:
    ptk = lang.proxy_import('omdev.ptk')
    ptk_md = lang.proxy_import('omdev.ptk.markdown')


##


@dc.dataclass(frozen=True)
class ChatState:
    name: str | None = None

    created_at: datetime.datetime = dc.field(default_factory=lang.utcnow)
    updated_at: datetime.datetime = dc.field(default_factory=lang.utcnow)

    chat: mc.Chat = ()


##


DEFAULT_CHAT_MODEL_BACKEND = 'openai'

CHAT_CHOICES_SERVICE_FACTORIES: ta.Mapping[str, ta.Callable[..., mc.ChatChoicesService]] = {}


##


ChatOption: ta.TypeAlias = mc.ChatChoicesOptions
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

        self._tool_executor = mc.NameSwitchedToolExecutor(col.make_map(
            (tn, mc.ToolFnToolExecutor(t.fn)) for tn, t in (tool_map or {}).items()
        ))

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

        backend = self._config.backend
        if backend is None:
            backend = DEFAULT_CHAT_MODEL_BACKEND

        if self._config.stream:
            with lang.maybe_managing(mc.registry_of[mc.ChatChoicesStreamService].new(backend)) as st_mdl:
                with st_mdl.invoke(mc.ChatChoicesStreamRequest(
                        chat,
                        (self._chat_options or []),
                )).v as st_resp:
                    lst: list[str] = []
                    for o in st_resp:
                        if o:
                            m = check.single(o).m
                            if m.s is not None:
                                print(m.s, end='', flush=True)
                                lst.append(m.s)
                            check.none(m.tool_exec_requests)
                    print()

                resp_m = mc.AiMessage(''.join(lst))
                chat.append(resp_m)

        else:
            csf: ta.Callable[..., mc.ChatChoicesService]
            if (bf := CHAT_CHOICES_SERVICE_FACTORIES.get(backend)) is not None:
                csf = bf
            else:
                csf = functools.partial(mc.registry_of[mc.ChatChoicesService].new, backend)

            with lang.maybe_managing(csf(
                    *([mc.ModelName(mn)] if (mn := self._config.model_name) is not None else []),
            )) as mdl:
                response = mdl.invoke(mc.ChatChoicesRequest(
                    chat,
                    (self._chat_options or []),
                ))

                resp_m = response.v[0].m
                chat.append(resp_m)

                if (trs := resp_m.tool_exec_requests):
                    check.state(resp_m.s is None)

                    tr: mc.ToolExecRequest = check.single(check.not_none(trs))
                    tool = check.not_none(self._tool_map)[check.non_empty_str(tr.name)]

                    tr_dct = dict(
                        id=tr.id,
                        spec=msh.marshal(tool.spec),
                        args=tr.args,
                    )
                    cr = ptk.strict_confirm(f'Execute requested tool?\n\n{json.dumps_pretty(tr_dct)}\n\n')

                    if not cr:
                        raise ToolExecutionRequestDeniedError

                    trm = mc.execute_tool_request(
                        mc.ToolContext(),
                        self._tool_executor,
                        tr,
                    )
                    chat.append(trm)

                    response = mdl.invoke(mc.ChatChoicesRequest(
                        chat,
                        (self._chat_options or []),
                    ))

                    resp_m = response.v[0].m
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
                print(check.isinstance(response.v[0].m.s, str).strip())

                state = dc.replace(
                    state,
                    chat=[
                        *state.chat,
                        response.v[0].m,
                    ],
                    updated_at=lang.utcnow(),
                )

                self._state_storage.save_state('chat', state, ChatState)
