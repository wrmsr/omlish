import abc
import typing as ta

from omlish import lang

from ... import minichain as mc


ServiceT = ta.TypeVar('ServiceT', bound=mc.Service)


##


BackendName = ta.NewType('BackendName', str)
DefaultBackendName = ta.NewType('DefaultBackendName', str)

BackendConfigs = ta.NewType('BackendConfigs', ta.Sequence['mc.Config'])


##


class BackendProvider(lang.Abstract, ta.Generic[ServiceT]):
    @abc.abstractmethod
    def provide_backend(self) -> ta.AsyncContextManager[ServiceT]:
        raise NotImplementedError
