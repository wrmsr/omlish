import typing as ta

from omlish import lang

from ..... import minichain as mc


##


ServerPort = ta.NewType('ServerPort', int)


class ChatStreamer(lang.Func1[mc.Chat, ta.Awaitable[ta.AsyncContextManager[ta.AsyncIterator[mc.AiDelta]]]]):
    pass
