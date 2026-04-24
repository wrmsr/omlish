import abc
import typing as ta

from omlish import lang

from .services import Service


ServiceT = ta.TypeVar('ServiceT', bound=Service)


##


class ServiceProvider(lang.Abstract, ta.Generic[ServiceT]):
    @abc.abstractmethod
    def provide_service(self) -> ta.AsyncContextManager[ServiceT]:
        raise NotImplementedError
