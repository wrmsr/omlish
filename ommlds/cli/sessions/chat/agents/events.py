import typing as ta

from omlish import dataclasses as dc
from omlish import lang

from ..... import minichain as mc


##


class ChatAgentEvent(lang.Abstract, lang.Sealed):
    pass


class ChatAgentEventSink(lang.Func1[ChatAgentEvent, ta.Awaitable[None]]):
    pass


##


@dc.dataclass(frozen=True)
class AiMessagesChatAgentEvent(ChatAgentEvent, lang.Final):
    chat: mc.Chat
