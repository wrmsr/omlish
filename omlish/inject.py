import abc
import dataclasses as dc
import typing as ta

from . import check


@dc.dataclass(frozen=True)
class Key:
    cls: type
    arr: bool = False
    tag: ta.Any = None


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
class SimpleProvider(Provider):
    cls: type
    fn: ProviderFn

    def provided_cls(self, rec: ta.Callable[[Key], type]) -> type:
        return self.cls

    def provider_fn(self) -> ProviderFn:
        return self.fn


@dc.dataclass(frozen=True)
class Binding:
    key: Key
    provider: Provider


Bindings = ta.Iterable[Binding]


def _build_provider_map(bs: Bindings) -> ta.Mapping[Key, Provider]:
    pm: ta.Dict[Key, Provider] = {}
    am: ta.Dict[Key, ta.List[Provider]] = {}
    for b in bs:
        if b.key.arr:
            am.setdefault(b.key, []).append(b.provider)
        else:
            if b.key in pm:
                raise KeyError(b.key)
            pm[b.key] = b.provider
    if am:
        raise NotImplementedError
    return pm


class Injector:
    def __init__(self, bs: Bindings, p: ta.Optional['Injector'] = None) -> None:
        super().__init__()

        self._bs = bs
        self._p = check.isinstance(p, (Injector, type(None)))

        self._pfm = {k: v.provider_fn() for k, v in _build_provider_map(bs).items()}

    def try_provide(self, key: ta.Any) -> ta.Any:
        check.isinstance(key, Key)
        fn = self._pfm.get(key)
        if fn is None:
            return None
        return fn(self)
