import abc
import typing as ta
import uuid

from omlish import lang
from omlish import typedvalues as tv

from ..... import minichain as mc


##


class ChatDriverId(tv.UniqueScalarTypedValue[uuid.UUID]):
    pass


class ChatDriverGetter(lang.Func0[ta.Awaitable['ChatDriver']]):
    pass


class ChatDriver(lang.Abstract):
    async def start(self) -> None:
        pass

    async def stop(self) -> None:
        pass

    @abc.abstractmethod
    def send_user_messages(self, next_user_chat: 'mc.UserChat') -> ta.Awaitable[None]:
        raise NotImplementedError
