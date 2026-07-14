import typing as ta

from omcore import lang

from ...... import minichain as mc


##


class ChatStreamer(lang.Func1[mc.Chat, ta.Awaitable[ta.AsyncContextManager[ta.AsyncIterator[mc.AiDelta]]]]):
    pass
