import typing as ta

from omlish import dataclasses as dc
from omlish import lang

from ...chat.messages import Chat
from ...chat.messages import UserChat
from ...chat.stream.types import AiDelta


##


class ChatEvent(lang.Abstract, lang.Sealed):
    pass


class ChatEventCallback(lang.Func1[ChatEvent, ta.Awaitable[None]]):
    pass


ChatEventCallbacks = ta.NewType('ChatEventCallbacks', ta.Sequence[ChatEventCallback])


##


@dc.dataclass(frozen=True)
class UserMessagesChatEvent(ChatEvent, lang.Final):
    chat: UserChat


@dc.dataclass(frozen=True)
class AiMessagesChatEvent(ChatEvent, lang.Final):
    chat: Chat

    _: dc.KW_ONLY

    streamed: bool = False


@dc.dataclass(frozen=True)
class AiDeltaChatEvent(ChatEvent, lang.Final):
    delta: AiDelta


@dc.dataclass(frozen=True)
class ErrorChatEvent(ChatEvent, lang.Final):
    message: str | None = None
    error: BaseException | None = None
