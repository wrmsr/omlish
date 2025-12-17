import typing as ta

from omlish import dataclasses as dc
from omlish import lang

from ...... import minichain as mc


##


class ChatEvent(lang.Abstract, lang.Sealed):
    pass


class ChatEventCallback(lang.Func1[ChatEvent, ta.Awaitable[None]]):
    pass


ChatEventCallbacks = ta.NewType('ChatEventCallbacks', ta.Sequence[ChatEventCallback])


##


@dc.dataclass(frozen=True)
class UserMessagesChatEvent(ChatEvent, lang.Final):
    chat: 'mc.UserChat'


@dc.dataclass(frozen=True)
class AiMessagesChatEvent(ChatEvent, lang.Final):
    chat: 'mc.Chat'


@dc.dataclass(frozen=True)
class AiDeltaChatEvent(ChatEvent, lang.Final):
    delta: 'mc.AiDelta'
