import typing as ta

from omlish import dataclasses as dc
from omlish import lang

from ...chat.messages import Chat
from ...chat.messages import ToolUseResultMessage
from ...chat.messages import UserChat
from ...chat.stream.types import AiDelta
from ...tools.types import ToolUse


##


class Event(lang.Abstract, lang.Sealed):
    pass


class EventCallback(lang.Func1[Event, ta.Awaitable[None]]):
    pass


EventCallbacks = ta.NewType('EventCallbacks', ta.Sequence[EventCallback])


##


@dc.dataclass(frozen=True)
class UserMessagesEvent(Event, lang.Final):
    chat: UserChat


#


@dc.dataclass(frozen=True)
class AiMessagesEvent(Event, lang.Final):
    chat: Chat

    _: dc.KW_ONLY

    streamed: bool = False


#


@dc.dataclass(frozen=True)
class AiStreamBeginEvent(Event, lang.Final):
    pass


@dc.dataclass(frozen=True)
class AiStreamDeltaEvent(Event, lang.Final):
    delta: AiDelta


@dc.dataclass(frozen=True)
class AiStreamEndEvent(Event, lang.Final):
    pass


#


@dc.dataclass(frozen=True)
class ErrorEvent(Event, lang.Final):
    message: str | None = None
    error: BaseException | None = None


#


@dc.dataclass(frozen=True)
class ToolUseEvent(Event, lang.Final):
    use: ToolUse


@dc.dataclass(frozen=True)
class ToolUseResultEvent(Event, lang.Final):
    message: ToolUseResultMessage
