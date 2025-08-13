import typing as ta

from omlish import dataclasses as dc
from omlish import inject as inj
from omlish import lang

from .base import ChatOption
from .base import ChatOptions
from .base import ChatSession
from .printing import ChatSessionPrinter
from .printing import MarkdownStringChatSessionPrinter
from .printing import SimpleStringChatSessionPrinter
from .state import ChatStateManager
from .state import StateStorageChatStateManager
from .tools import AskingToolExecutionConfirmation
from .tools import NopToolExecutionConfirmation
from .tools import ToolExecRequestExecutor
from .tools import ToolExecRequestExecutorImpl
from .tools import ToolExecutionConfirmation


##


@dc.dataclass(frozen=True, eq=False)
class _InjectedChatOptions:
    v: ChatOptions


def bind_chat_options(*cos: ChatOption) -> inj.Elements:
    return inj.bind_set_entry_const(ta.AbstractSet[_InjectedChatOptions], _InjectedChatOptions(ChatOptions(cos)))


##


def bind_chat_session(cfg: ChatSession.Config) -> inj.Elements:
    els: list[inj.Elemental] = []

    #

    els.extend([
        inj.set_binder[_InjectedChatOptions](),
        inj.bind(
            lang.typed_lambda(ChatOptions, s=ta.AbstractSet[_InjectedChatOptions])(
                lambda s: ChatOptions([
                    co
                    for ico in s
                    for co in ico.v
                ]),
            ),
            singleton=True,
        ),
    ])

    #

    els.extend([
        inj.bind(StateStorageChatStateManager, singleton=True),
        inj.bind(ChatStateManager, to_key=StateStorageChatStateManager),
    ])

    #

    if cfg.markdown:
        els.extend([
            inj.bind(MarkdownStringChatSessionPrinter, singleton=True),
            inj.bind(ChatSessionPrinter, to_key=MarkdownStringChatSessionPrinter),
        ])
    else:
        els.extend([
            inj.bind(SimpleStringChatSessionPrinter, singleton=True),
            inj.bind(ChatSessionPrinter, to_key=SimpleStringChatSessionPrinter),
        ])

    #

    if cfg.dangerous_no_tool_confirmation:
        els.extend([
            inj.bind(NopToolExecutionConfirmation, singleton=True),
            inj.bind(ToolExecutionConfirmation, to_key=NopToolExecutionConfirmation),
        ])
    else:
        els.extend([
            inj.bind(AskingToolExecutionConfirmation, singleton=True),
            inj.bind(ToolExecutionConfirmation, to_key=AskingToolExecutionConfirmation),
        ])

    #

    els.extend([
        inj.bind(ToolExecRequestExecutorImpl, singleton=True),
        inj.bind(ToolExecRequestExecutor, to_key=ToolExecRequestExecutorImpl),
    ])

    #

    return inj.as_elements(*els)
