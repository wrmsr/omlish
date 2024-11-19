"""
injector.py
"""
import abc
import dataclasses as dc
import functools
import inspect
import types
import typing as ta
import weakref

from omlish.lite.check import check_isinstance
from omlish.lite.check import check_not_isinstance
from omlish.lite.check import check_not_none
from omlish.lite.maybes import Maybe
from omlish.lite.reflect import get_optional_alias_arg
from omlish.lite.reflect import is_optional_alias


T = ta.TypeVar('T')


###
# types.py


@dc.dataclass(frozen=True)
class Key:
    cls: type
    tag: ta.Any = None
    array: bool = False


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


###
# exceptions.py


@dc.dataclass(frozen=True)
class KeyException(Exception):
    key: Key

    source: ta.Any = None
    name: ta.Optional[str] = None


@dc.dataclass(frozen=True)
class UnboundKeyException(KeyException):
    pass


@dc.dataclass(frozen=True)
class DuplicateKeyException(KeyException):
    pass


###
# keys.py


def as_key(o: ta.Any) -> Key:
    if o is inspect.Parameter.empty:
        raise TypeError(o)
    if isinstance(o, Key):
        return o
    if isinstance(o, type):
        return Key(o)
    raise TypeError(o)


##


def array(o: ta.Any) -> Key:
    return dc.replace(as_key(o), array=True)


def tag(o: ta.Any, t: ta.Any) -> Key:
    return dc.replace(as_key(o), tag=t)


###
# providers.py


@dc.dataclass(frozen=True)
class FnProvider(Provider):
    fn: ta.Any


    def __post_init__(self) -> None:
        check_not_isinstance(self.fn, type)

    def provider_fn(self) -> ProviderFn:
        def pfn(i: Injector) -> ta.Any:
            return i.inject(self.fn)

        return pfn


@dc.dataclass(frozen=True)
class CtorProvider(Provider):
    cls: type

    def __post_init__(self) -> None:
        check_isinstance(self.cls, type)

    def provider_fn(self) -> ProviderFn:
        def pfn(i: Injector) -> ta.Any:
            return i.inject(self.cls)

        return pfn


@dc.dataclass(frozen=True)
class ConstProvider(Provider):
    v: ta.Any

    def provider_fn(self) -> ProviderFn:
        return lambda _: self.v


@dc.dataclass(frozen=True)
class SingletonProvider(Provider):
    p: Provider

    def __post_init__(self) -> None:
        check_isinstance(self.p, Provider)

    def provider_fn(self) -> ProviderFn:
        v = not_set = object()

        def pfn(i: Injector) -> ta.Any:
            nonlocal v
            if v is not_set:
                v = ufn(i)
            return v

        ufn = self.p.provider_fn()
        return pfn


@dc.dataclass(frozen=True)
class LinkProvider(Provider):
    k: Key

    def __post_init__(self) -> None:
        check_isinstance(self.k, Key)

    def provider_fn(self) -> ProviderFn:
        def pfn(i: Injector) -> ta.Any:
            return i.provide(self.k)

        return pfn


@dc.dataclass(frozen=True)
class ArrayProvider(Provider):
    ty: type
    ps: ta.Sequence[Provider]

    def provider_fn(self) -> ProviderFn:
        ps = [p.provider_fn() for p in self.ps]

        def pfn(i: Injector) -> ta.Any:
            rv = []
            for ep in ps:
                o = ep(i)
                rv.append(o)
            return rv

        return pfn


###
# bindings.py


@dc.dataclass(frozen=True)
class _Bindings(Bindings):
    bs: ta.Optional[ta.Sequence[Binding]] = None
    ps: ta.Optional[ta.Sequence[Bindings]] = None

    def bindings(self) -> ta.Iterator[Binding]:
        if self.bs is not None:
            yield from self.bs
        if self.ps is not None:
            for p in self.ps:
                yield from p.bindings()


def as_bindings(*vs: ta.Any) -> Bindings:
    bs: list[Binding] = []
    ps: list[Bindings] = []
    for a in vs:
        if isinstance(a, Bindings):
            ps.append(a)
        elif isinstance(a, Binding):
            bs.append(a)
        else:
            raise TypeError(a)
    return _Bindings(
        bs or None,
        ps or None,
        )


##


@dc.dataclass(frozen=True)
class _Overrides(Bindings):
    p: Bindings
    m: ta.Mapping[Key, Binding]

    def bindings(self) -> ta.Iterator[Binding]:
        for b in self.p.bindings():
            yield self.m.get(b.key, b)


def override(p: Bindings, *a: ta.Any) -> Bindings:
    m: dict[Key, Binding] = {}
    for b in as_bindings(*a).bindings():
        if b.key in m:
            raise DuplicateKeyException(b.key)
        m[b.key] = b
    return _Overrides(p, m)


##


def build_provider_map(bs: Bindings) -> ta.Mapping[Key, Provider]:
    pm: dict[Key, Provider] = {}
    am: dict[Key, list[Provider]] = {}
    for b in bs.bindings():
        if b.key.array:
            am.setdefault(b.key, []).append(b.provider)
        else:
            if b.key in pm:
                raise KeyError(b.key)
            pm[b.key] = b.provider
    if am:
        for k, aps in am.items():
            pm[k] = ArrayProvider(k.cls, aps)

    return pm


###
# inspect.py


_SIGNATURE_CACHE: ta.MutableMapping[ta.Any, inspect.Signature] = weakref.WeakKeyDictionary()


def signature(obj: ta.Any) -> inspect.Signature:
    try:
        return _SIGNATURE_CACHE[obj]
    except TypeError:
        return inspect.signature(obj)
    except KeyError:
        pass
    sig = inspect.signature(obj)
    _SIGNATURE_CACHE[obj] = sig
    return sig


class Kwarg(ta.NamedTuple):
    name: str
    key: Key
    has_default: bool


class KwargsTarget(ta.NamedTuple):
    obj: ta.Any
    kwargs: ta.Sequence[Kwarg]


def build_kwargs_target(
        obj: ta.Any,
        *,
        skip_args: int = 0,
        skip_kwargs: ta.Optional[ta.Iterable[ta.Any]] = None,
        raw_optional: bool = False,
) -> KwargsTarget:
    sig = signature(obj)

    seen: set[Key] = set(map(as_key, skip_kwargs)) if skip_kwargs is not None else set()
    kws: list[Kwarg] = []
    for p in list(sig.parameters.values())[skip_args:]:
        if p.annotation is inspect.Signature.empty:
            if p.default is not inspect.Parameter.empty:
                raise KeyError(f'{obj}, {p.name}')
            continue

        if p.kind not in (inspect.Parameter.POSITIONAL_OR_KEYWORD, inspect.Parameter.KEYWORD_ONLY):
            raise TypeError(sig)

        ann = p.annotation
        if (
                not raw_optional and
                is_optional_alias(ann)
        ):
            ann = get_optional_alias_arg(ann)

        k = as_key(ann)

        if k in seen:
            raise DuplicateKeyException(k)
        seen.add(k)

        kws.append(Kwarg(
            p.name,
            k,
            p.default is not inspect.Parameter.empty,
            ))

    return KwargsTarget(
        obj,
        kws,
    )


###
#


_FN_TYPES: tuple[type, ...] = (
    types.FunctionType,
    types.MethodType,

    classmethod,
    staticmethod,

    functools.partial,
    functools.partialmethod,
)


def _is_fn(obj: ta.Any) -> bool:
    return isinstance(obj, _FN_TYPES)


def bind_as_fn(cls: type[T]) -> type[T]:
    check_isinstance(cls, type)
    global _FN_TYPES
    if cls not in _FN_TYPES:
        _FN_TYPES = (*_FN_TYPES, cls)
    return cls


##


_BANNED_BIND_TYPES: tuple[type, ...] = (
    Provider,
)


def bind(
        obj: ta.Any,
        *,
        key: ta.Any = None,
        tag: ta.Any = None,
        array: ta.Optional[bool] = None,  # noqa

        to_fn: ta.Any = None,
        to_ctor: ta.Any = None,
        to_const: ta.Any = None,
        to_key: ta.Any = None,

        singleton: bool = False,
) -> Binding:
    if obj is None or obj is inspect.Parameter.empty:
        raise TypeError(obj)
    if isinstance(obj, _BANNED_BIND_TYPES):
        raise TypeError(obj)

    ##

    if key is not None:
        if isinstance(key, type):
            key = Key(key)
        elif not isinstance(key, Key):
            raise TypeError(key)

    ##

    has_to = (
            to_fn is not None or
            to_ctor is not None or
            to_const is not None or
            to_key is not None
    )
    if isinstance(obj, Key):
        if key is None:
            key = obj
    elif isinstance(obj, type):
        if not has_to:
            to_ctor = obj
        if key is None:
            key = Key(obj)
    elif _is_fn(obj) and not has_to:
        to_fn = obj
        if key is None:
            sig = signature(obj)
            ty = check_isinstance(sig.return_annotation, type)
            key = Key(ty)
    else:
        if to_const is not None:
            raise TypeError('Cannot bind instance with to_const')
        to_const = obj
        if key is None:
            key = Key(type(obj))
    del has_to

    ##

    if tag is not None:
        if key.tag is not None:
            raise TypeError('Tag already set')
        key = dc.replace(key, tag=tag)

    if array is not None:
        key = dc.replace(key, array=array)

    ##

    providers: list[Provider] = []
    if to_fn is not None:
        providers.append(FnProvider(to_fn))
    if to_ctor is not None:
        providers.append(CtorProvider(to_ctor))
    if to_const is not None:
        providers.append(ConstProvider(to_const))
    if to_key is not None:
        providers.append(LinkProvider(as_key(to_key)))
    if not providers:
        raise TypeError('Must specify provider')
    if len(providers) > 1:
        raise TypeError('May not specify multiple providers')
    provider, = providers

    ##

    if singleton:
        provider = SingletonProvider(provider)

    ##

    binding = Binding(key, provider)

    ##

    return binding


###
# injector.py


class _Injector(Injector):
    def __init__(self, bs: Bindings, p: ta.Optional[Injector] = None) -> None:
        super().__init__()

        self._bs = check_isinstance(bs, Bindings)
        self._p: ta.Optional[Injector] = check_isinstance(p, (Injector, type(None)))

        self._pfm = {k: v.provider_fn() for k, v in build_provider_map(bs).items()}

    def try_provide(self, key: ta.Any) -> Maybe[ta.Any]:
        key = as_key(key)

        fn = self._pfm.get(key)
        if fn is not None:
            return Maybe.just(fn(self))

        if self._p is not None:
            pv = self._p.try_provide(key)
            if pv is not None:
                return Maybe.empty()

        return Maybe.empty()

    def provide(self, key: ta.Any) -> ta.Any:
        v = self.try_provide(key)
        if v.present:
            return v.must()
        raise UnboundKeyException(key)

    def provide_kwargs(self, obj: ta.Any) -> ta.Mapping[str, ta.Any]:
        kt = build_kwargs_target(obj)
        ret: dict[str, ta.Any] = {}
        for kw in kt.kwargs:
            if kw.has_default:
                if not (mv := self.try_provide(kw.key)).present:
                    continue
                v = mv.must()
            else:
                v = self.provide(kw.key)
            ret[kw.name] = v
        return ret

    def inject(self, obj: ta.Any) -> ta.Any:
        kws = self.provide_kwargs(obj)
        return obj(**kws)


def create_injector(bs: Bindings, p: ta.Optional[Injector] = None) -> Injector:
    return _Injector(bs, p)
