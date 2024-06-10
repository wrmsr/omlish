import abc
import typing as ta

from .. import dataclasses as dc
from .. import lang


T = ta.TypeVar('T')


##


Cls = type | ta.NewType


@dc.dataclass(frozen=True)
class Key(lang.Final, ta.Generic[T]):
    cls: type[T] | ta.NewType
    arr: bool = False
    tag: ta.Any = None


##


ProviderFn = ta.Callable[['Injector'], ta.Any]
ProviderFnMap = ta.Mapping[Key, ProviderFn]


class Provider(abc.ABC):
    @abc.abstractmethod
    def provided_cls(self, rec: ta.Callable[[Key], Cls]) -> Cls:
        raise NotImplementedError

    @abc.abstractmethod
    def required_keys(self) -> frozenset[Key | None]:
        raise NotImplementedError

    @abc.abstractmethod
    def children(self) -> ta.Iterable['Provider']:
        raise NotImplementedError

    @abc.abstractmethod
    def provider_fn(self) -> ProviderFn:
        raise NotImplementedError


##


@dc.dataclass(frozen=True)
class Binding(lang.Final):
    key: Key
    provider: Provider


class Bindings(abc.ABC):
    @abc.abstractmethod
    def bindings(self) -> ta.Iterator[Binding]:
        raise NotImplementedError


Binder = ta.Callable[[], Bindings]


##


class _KeyGen(abc.ABC):
    @abc.abstractmethod
    def _gen_key(self) -> Key:
        raise NotImplementedError


class _ProviderGen(abc.ABC):
    @abc.abstractmethod
    def _gen_provider(self) -> Provider:
        raise NotImplementedError


class _BindingGen(abc.ABC):
    @abc.abstractmethod
    def _gen_binding(self) -> Binding:
        raise NotImplementedError


##


class Kwarg(ta.NamedTuple):
    name: str
    key: Key
    has_default: bool


class KwargsTarget(ta.NamedTuple):
    obj: ta.Any
    kwargs: ta.Sequence[Kwarg]


##


class Injector(abc.ABC):
    @abc.abstractmethod
    def try_provide(self, key: ta.Any) -> lang.Maybe[ta.Any]:
        raise NotImplementedError

    @abc.abstractmethod
    def provide(self, key: ta.Any) -> ta.Any:
        raise NotImplementedError

    @abc.abstractmethod
    def provide_kwargs(self, kt: KwargsTarget) -> ta.Mapping[str, ta.Any]:
        raise NotImplementedError

    @abc.abstractmethod
    def inject(self, obj: ta.Any) -> ta.Any:
        raise NotImplementedError

    def __getitem__(
            self,
            target: ta.Union[Key[T], type[T]],
    ) -> T:
        return self.provide(target)
