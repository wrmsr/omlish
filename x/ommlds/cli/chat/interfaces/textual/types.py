import typing as ta

from omcore import lang


if ta.TYPE_CHECKING:
    from .app import ChatApp  # noqa


##


class ChatAppGetter(lang.AsyncCachedFunc0['ChatApp']):
    pass
