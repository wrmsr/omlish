import typing as ta

from omlish import lang


if ta.TYPE_CHECKING:
    from .interface import ChatDriverInterface  # noqa


##


class ChatDriverInterfaceGetter(lang.AsyncCachedFunc0['ChatDriverInterface']):
    pass
