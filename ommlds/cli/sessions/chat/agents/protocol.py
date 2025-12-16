import typing as ta

from omlish import dataclasses as dc
from omlish import lang

from ..... import minichain as mc


##


class ChatAgentInput(lang.Abstract, lang.Sealed):
    pass


@dc.dataclass(frozen=True)
class UserMessagesChatAgentInput(ChatAgentInput, lang.Final):
    chat: mc.UserChat


##


class ChatAgentOutput(lang.Abstract, lang.Sealed):
    pass


ChatAgentOutputSink: ta.TypeAlias = ta.Callable[[ChatAgentOutput], ta.Awaitable[None]]


@dc.dataclass(frozen=True)
class AiMessagesChatAgentOutput(ChatAgentOutput, lang.Final):
    chat: mc.Chat
