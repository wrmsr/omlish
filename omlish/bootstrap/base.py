import abc
import dataclasses as dc
import typing as ta

from omlish import lang


BootstrapConfigT = ta.TypeVar('BootstrapConfigT', bound='Bootstrap.Config')


##


class Bootstrap(abc.ABC, lang.PackageSealed, ta.Generic[BootstrapConfigT]):
    @dc.dataclass(frozen=True)
    class Config(abc.ABC):  # noqa
        pass

    def __init__(self, config: BootstrapConfigT) -> None:
        super().__init__()
        self._config = config

    def __init_subclass__(cls, **kwargs: ta.Any) -> None:
        super().__init_subclass__(**kwargs)
        if not cls.__name__.endswith('Bootstrap'):
            raise NameError(cls)
        if abc.ABC not in cls.__bases__ and not issubclass(cls.__dict__['Config'], Bootstrap.Config):
            raise TypeError(cls)


class SimpleBootstrap(Bootstrap[BootstrapConfigT], abc.ABC):
    @abc.abstractmethod
    def run(self) -> None:
        raise NotImplementedError


class ContextBootstrap(Bootstrap[BootstrapConfigT], abc.ABC):
    @abc.abstractmethod
    def enter(self) -> ta.ContextManager[None]:
        raise NotImplementedError
