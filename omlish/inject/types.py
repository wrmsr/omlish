import abc
import dataclasses as dc
import typing as ta


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
    def provided_cls(self, rec: ta.Callable[[Key], type]) -> type:
        raise NotImplementedError

    @abc.abstractmethod
    def provider_fn(self) -> ProviderFn:
        raise NotImplementedError


##


@dc.dataclass(frozen=True)
class Binding:
    key: Key
    provider: Provider


Bindings = ta.Iterable[Binding]

Binder = ta.Callable[[], Bindings]


##


class _BindingGen(abc.ABC):
    @abc.abstractmethod
    def binding(self) -> Binding:
        raise NotImplementedError


class _ProviderGen(abc.ABC):
    @abc.abstractmethod
    def provider(self) -> Provider:
        raise NotImplementedError


##


class Injector(abc.ABC):
    @abc.abstractmethod
    def try_provide(self, key: ta.Any) -> ta.Any:
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
