import abc
import typing as ta

from omlish import lang

from ..... import minichain as mc


ServiceT = ta.TypeVar('ServiceT', bound=mc.Service)


##


BackendName = ta.NewType('BackendName', str)
BackendConfigs = ta.NewType('BackendConfigs', ta.Sequence['mc.Config'])


##


class BackendProvider(lang.Abstract, ta.Generic[ServiceT]):
    @abc.abstractmethod
    def provide_backend(self) -> ta.AsyncContextManager[ServiceT]:
        raise NotImplementedError


##


class ChatChoicesServiceBackendProvider(BackendProvider['mc.ChatChoicesService'], lang.Abstract):
    pass


class ChatChoicesStreamServiceBackendProvider(BackendProvider['mc.ChatChoicesStreamService'], lang.Abstract):
    pass
