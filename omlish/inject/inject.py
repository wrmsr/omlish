import abc
import dataclasses as dc
import typing as ta

from .. import check
from .. import lang


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
class FnProvider(Provider):
    cls: type
    fn: ProviderFn

    def provided_cls(self, rec: ta.Callable[[Key], type]) -> type:
        return self.cls

    def provider_fn(self) -> ProviderFn:
        return self.fn


@dc.dataclass(frozen=True)
class ConstProvider(Provider):
    cls: type
    v: ta.Any

    def provided_cls(self, rec: ta.Callable[[Key], type]) -> type:
        return self.cls

    def provider_fn(self) -> ProviderFn:
        return lambda _: self.v


@dc.dataclass(frozen=True)
class SingletonProvider(Provider):
    p: Provider

    def provided_cls(self, rec: ta.Callable[[Key], type]) -> type:
        return self.p.provided_cls(rec)

    def provider_fn(self) -> ProviderFn:
        def fn(i):
            nonlocal v
            if v is not_set:
                v = pfn(i)
            return v

        pfn = self.p.provider_fn()
        v = not_set = object()
        return fn


@dc.dataclass(frozen=True)
class Binding:
    key: Key
    provider: Provider


Bindings = ta.Iterable[Binding]

Binder = ta.Callable[[], Bindings]


class _BindingGen(abc.ABC):
    @abc.abstractmethod
    def binding(self) -> Binding:
        raise NotImplementedError


class _ProviderGen(abc.ABC):
    @abc.abstractmethod
    def provider(self) -> Provider:
        raise NotImplementedError


def _as_provider(o: ta.Any) -> Provider:
    return ConstProvider(type(o), o)


def _as_binding(o: ta.Any) -> Binding:
    check.not_none(o)
    # check.not_isinstance(o, Bindings)
    if isinstance(o, Binding):
        return o
    if isinstance(o, _BindingGen):
        return o.binding()
    if isinstance(o, Provider):
        return Binding(Key(o.provided_cls(lambda _: lang.raise_(TypeError(o)))), o)
    if isinstance(o, _ProviderGen):
        return _as_binding(o.provider())
    cls = type(o)
    return Binding(Key(cls), ConstProvider(cls, o))


def bind(*args: ta.Any) -> Binder:
    raise NotImplementedError


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
