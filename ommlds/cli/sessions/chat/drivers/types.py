import abc
import typing as ta
import uuid

from omlish import dataclasses as dc
from omlish import lang
from omlish import typedvalues as tv

from ..... import minichain as mc


##


@dc.dataclass(frozen=True)
class ProvidedSystemMessage:
    c: 'mc.Content'

    _: dc.KW_ONLY

    priority: int | None = None


class SystemMessageProvider(lang.Abstract):
    @abc.abstractmethod
    def provide_system_messages(self) -> ta.Awaitable[ta.Sequence[ProvidedSystemMessage]]:
        raise NotImplementedError


SystemMessageProviders = ta.NewType('SystemMessageProviders', ta.Sequence[SystemMessageProvider])


##


class PlaceholderContentsProvider(lang.Abstract):
    @abc.abstractmethod
    def provide_placeholder_contents(self) -> ta.Awaitable['mc.PlaceholderContents']:
        raise NotImplementedError


PlaceholderContentsProviders = ta.NewType('PlaceholderContentsProviders', ta.Sequence[PlaceholderContentsProvider])


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
