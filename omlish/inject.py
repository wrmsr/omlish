import abc
import dataclasses as dc
import typing as ta

from . import check


@dc.dataclass(frozen=True)
class Key:
    cls: type
    arr: bool
    tag: ta.Any


ProviderFn = ta.Callable[['Injector'], ta.Any]
ProviderFnMap = ta.Mapping[Key, ProviderFn]


class Provider(abc.ABC):
    @abc.abstractmethod
    def provided_cls(self, rec: ta.Callable[[Key], type]) -> type:
        raise NotImplementedError

    @abc.abstractmethod
    def provider_fn(self) -> ProviderFn:
        raise NotImplementedError


@dc.dataclass(frozen=True)
class Binding:
    key: Key
    provider: Provider


Bindings = ta.Iterable[Binding]


class Injector:
    def __init__(self, bs: Bindings, p: ta.Optional['Injector'] = None) -> None:
        super().__init__()
        self._bs = bs
        self._p = check.isinstance(p, (Injector, type(None)))

    def provide(self, key: ta.Any) -> ta.Any:
        raise NotImplementedError
