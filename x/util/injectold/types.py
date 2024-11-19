import abc
import dataclasses as dc
import typing as ta

from omlish.lite.maybes import Maybe


##


@dc.dataclass(frozen=True)
class Key:
    cls: type
    arr: bool = False
    tag: ta.Any = None


##


ProviderFn = ta.Callable[['Injector'], ta.Any]
ProviderFnMap = ta.Mapping[Key, ProviderFn]


class Provider(abc.ABC):
    @abc.abstractmethod
    def provider_fn(self) -> ProviderFn:
        raise NotImplementedError


##


@dc.dataclass(frozen=True)
class Binding:
    key: Key
    provider: Provider


class Bindings(abc.ABC):
    @abc.abstractmethod
    def bindings(self) -> ta.Iterator[Binding]:
        raise NotImplementedError


Binder = ta.Callable[[], Bindings]


##


class Injector(abc.ABC):
    @abc.abstractmethod
    def try_provide(self, key: ta.Any) -> Maybe[ta.Any]:
        raise NotImplementedError

    @abc.abstractmethod
    def provide(self, key: ta.Any) -> ta.Any:
        raise NotImplementedError

    @abc.abstractmethod
    def provide_kwargs(self, obj: ta.Any) -> ta.Mapping[str, ta.Any]:
        raise NotImplementedError

    @abc.abstractmethod
    def inject(self, obj: ta.Any) -> ta.Any:
        raise NotImplementedError
