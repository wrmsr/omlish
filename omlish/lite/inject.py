# ruff: noqa: UP006 UP007
import abc
import dataclasses as dc
import functools
import inspect
import types
import typing as ta
import weakref

from omlish.lite.check import check_isinstance
from omlish.lite.check import check_not_isinstance
from omlish.lite.maybes import Maybe
from omlish.lite.reflect import get_optional_alias_arg
from omlish.lite.reflect import is_optional_alias


T = ta.TypeVar('T')


###
# types


@dc.dataclass(frozen=True)
class InjectorKey:
    cls: type
    tag: ta.Any = None
    array: bool = False


##


InjectorProviderFn = ta.Callable[['Injector'], ta.Any]
InjectorProviderFnMap = ta.Mapping[InjectorKey, InjectorProviderFn]


class InjectorProvider(abc.ABC):
    @abc.abstractmethod
    def provider_fn(self) -> InjectorProviderFn:
        raise NotImplementedError


##


@dc.dataclass(frozen=True)
class InjectorBinding:
    key: InjectorKey
    provider: InjectorProvider


class InjectorBindings(abc.ABC):
    @abc.abstractmethod
    def bindings(self) -> ta.Iterator[InjectorBinding]:
        raise NotImplementedError


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
# exceptions


@dc.dataclass(frozen=True)
class InjectorKeyError(Exception):
    key: InjectorKey

    source: ta.Any = None
    name: ta.Optional[str] = None


@dc.dataclass(frozen=True)
class UnboundInjectorKeyError(InjectorKeyError):
    pass


@dc.dataclass(frozen=True)
class DuplicateInjectorKeyError(InjectorKeyError):
    pass


###
# keys


def as_injector_key(o: ta.Any) -> InjectorKey:
    if o is inspect.Parameter.empty:
        raise TypeError(o)
    if isinstance(o, InjectorKey):
        return o
    if isinstance(o, type):
        return InjectorKey(o)
    raise TypeError(o)


###
# providers


@dc.dataclass(frozen=True)
class FnInjectorProvider(InjectorProvider):
    fn: ta.Any

    def __post_init__(self) -> None:
        check_not_isinstance(self.fn, type)

    def provider_fn(self) -> InjectorProviderFn:
        def pfn(i: Injector) -> ta.Any:
            return i.inject(self.fn)

        return pfn


@dc.dataclass(frozen=True)
class CtorInjectorProvider(InjectorProvider):
    cls: type

    def __post_init__(self) -> None:
        check_isinstance(self.cls, type)

    def provider_fn(self) -> InjectorProviderFn:
        def pfn(i: Injector) -> ta.Any:
            return i.inject(self.cls)

        return pfn


@dc.dataclass(frozen=True)
class ConstInjectorProvider(InjectorProvider):
    v: ta.Any

    def provider_fn(self) -> InjectorProviderFn:
        return lambda _: self.v


@dc.dataclass(frozen=True)
class SingletonInjectorProvider(InjectorProvider):
    p: InjectorProvider

    def __post_init__(self) -> None:
        check_isinstance(self.p, InjectorProvider)

    def provider_fn(self) -> InjectorProviderFn:
        v = not_set = object()

        def pfn(i: Injector) -> ta.Any:
            nonlocal v
            if v is not_set:
                v = ufn(i)
            return v

        ufn = self.p.provider_fn()
        return pfn


@dc.dataclass(frozen=True)
class LinkInjectorProvider(InjectorProvider):
    k: InjectorKey

    def __post_init__(self) -> None:
        check_isinstance(self.k, InjectorKey)

    def provider_fn(self) -> InjectorProviderFn:
        def pfn(i: Injector) -> ta.Any:
            return i.provide(self.k)

        return pfn


@dc.dataclass(frozen=True)
class ArrayInjectorProvider(InjectorProvider):
    ty: type
    ps: ta.Sequence[InjectorProvider]

    def provider_fn(self) -> InjectorProviderFn:
        ps = [p.provider_fn() for p in self.ps]

        def pfn(i: Injector) -> ta.Any:
            rv = []
            for ep in ps:
                o = ep(i)
                rv.append(o)
            return rv

        return pfn


###
# bindings


@dc.dataclass(frozen=True)
class _InjectorBindings(InjectorBindings):
    bs: ta.Optional[ta.Sequence[InjectorBinding]] = None
    ps: ta.Optional[ta.Sequence[InjectorBindings]] = None

    def bindings(self) -> ta.Iterator[InjectorBinding]:
        if self.bs is not None:
            yield from self.bs
        if self.ps is not None:
            for p in self.ps:
                yield from p.bindings()


def as_injector_bindings(*vs: ta.Any) -> InjectorBindings:
    bs: ta.List[InjectorBinding] = []
    ps: ta.List[InjectorBindings] = []
    for a in vs:
        if isinstance(a, InjectorBindings):
            ps.append(a)
        elif isinstance(a, InjectorBinding):
            bs.append(a)
        else:
            raise TypeError(a)
    return _InjectorBindings(
        bs or None,
        ps or None,
    )


##


@dc.dataclass(frozen=True)
class OverridesInjectorBindings(InjectorBindings):
    p: InjectorBindings
    m: ta.Mapping[InjectorKey, InjectorBinding]

    def bindings(self) -> ta.Iterator[InjectorBinding]:
        for b in self.p.bindings():
            yield self.m.get(b.key, b)


def injector_override(p: InjectorBindings, *a: ta.Any) -> InjectorBindings:
    m: ta.Dict[InjectorKey, InjectorBinding] = {}
    for b in as_injector_bindings(*a).bindings():
        if b.key in m:
            raise DuplicateInjectorKeyError(b.key)
        m[b.key] = b
    return OverridesInjectorBindings(p, m)


##


def build_injector_provider_map(bs: InjectorBindings) -> ta.Mapping[InjectorKey, InjectorProvider]:
    pm: ta.Dict[InjectorKey, InjectorProvider] = {}
    am: ta.Dict[InjectorKey, ta.List[InjectorProvider]] = {}
    for b in bs.bindings():
        if b.key.array:
            am.setdefault(b.key, []).append(b.provider)
        else:
            if b.key in pm:
                raise KeyError(b.key)
            pm[b.key] = b.provider
    if am:
        for k, aps in am.items():
            pm[k] = ArrayInjectorProvider(k.cls, aps)

    return pm


###
# inspection


_INJECTION_SIGNATURE_CACHE: ta.MutableMapping[ta.Any, inspect.Signature] = weakref.WeakKeyDictionary()


def _injection_signature(obj: ta.Any) -> inspect.Signature:
    try:
        return _INJECTION_SIGNATURE_CACHE[obj]
    except TypeError:
        return inspect.signature(obj)
    except KeyError:
        pass
    sig = inspect.signature(obj)
    _INJECTION_SIGNATURE_CACHE[obj] = sig
    return sig


class InjectionKwarg(ta.NamedTuple):
    name: str
    key: InjectorKey
    has_default: bool


class InjectionKwargsTarget(ta.NamedTuple):
    obj: ta.Any
    kwargs: ta.Sequence[InjectionKwarg]


def build_injection_kwargs_target(
        obj: ta.Any,
        *,
        skip_args: int = 0,
        skip_kwargs: ta.Optional[ta.Iterable[ta.Any]] = None,
        raw_optional: bool = False,
) -> InjectionKwargsTarget:
    sig = _injection_signature(obj)

    seen: ta.Set[InjectorKey] = set(map(as_injector_key, skip_kwargs)) if skip_kwargs is not None else set()
    kws: ta.List[InjectionKwarg] = []
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

        k = as_injector_key(ann)

        if k in seen:
            raise DuplicateInjectorKeyError(k)
        seen.add(k)

        kws.append(InjectionKwarg(
            p.name,
            k,
            p.default is not inspect.Parameter.empty,
        ))

    return InjectionKwargsTarget(
        obj,
        kws,
    )


###
# binder


class InjectorBinder:
    def __new__(cls, *args, **kwargs):  # noqa
        raise TypeError

    _FN_TYPES: ta.Tuple[type, ...] = (
        types.FunctionType,
        types.MethodType,

        classmethod,
        staticmethod,

        functools.partial,
        functools.partialmethod,
    )

    @classmethod
    def _is_fn(cls, obj: ta.Any) -> bool:
        return isinstance(obj, cls._FN_TYPES)

    @classmethod
    def bind_as_fn(cls, icls: ta.Type[T]) -> ta.Type[T]:
        check_isinstance(icls, type)
        if icls not in cls._FN_TYPES:
            cls._FN_TYPES = (*cls._FN_TYPES, icls)
        return icls

    _BANNED_BIND_TYPES: ta.Tuple[type, ...] = (
        InjectorProvider,
    )

    @classmethod
    def bind(
            cls,
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
    ) -> InjectorBinding:
        if obj is None or obj is inspect.Parameter.empty:
            raise TypeError(obj)
        if isinstance(obj, cls._BANNED_BIND_TYPES):
            raise TypeError(obj)

        ##

        if key is not None:
            if isinstance(key, type):
                key = InjectorKey(key)
            elif not isinstance(key, InjectorKey):
                raise TypeError(key)

        ##

        has_to = (
            to_fn is not None or
            to_ctor is not None or
            to_const is not None or
            to_key is not None
        )
        if isinstance(obj, InjectorKey):
            if key is None:
                key = obj
        elif isinstance(obj, type):
            if not has_to:
                to_ctor = obj
            if key is None:
                key = InjectorKey(obj)
        elif cls._is_fn(obj) and not has_to:
            to_fn = obj
            if key is None:
                sig = _injection_signature(obj)
                ty = check_isinstance(sig.return_annotation, type)
                key = InjectorKey(ty)
        else:
            if to_const is not None:
                raise TypeError('Cannot bind instance with to_const')
            to_const = obj
            if key is None:
                key = InjectorKey(type(obj))
        del has_to

        ##

        if tag is not None:
            if key.tag is not None:
                raise TypeError('Tag already set')
            key = dc.replace(key, tag=tag)

        if array is not None:
            key = dc.replace(key, array=array)

        ##

        providers: ta.List[InjectorProvider] = []
        if to_fn is not None:
            providers.append(FnInjectorProvider(to_fn))
        if to_ctor is not None:
            providers.append(CtorInjectorProvider(to_ctor))
        if to_const is not None:
            providers.append(ConstInjectorProvider(to_const))
        if to_key is not None:
            providers.append(LinkInjectorProvider(as_injector_key(to_key)))
        if not providers:
            raise TypeError('Must specify provider')
        if len(providers) > 1:
            raise TypeError('May not specify multiple providers')
        provider, = providers

        ##

        if singleton:
            provider = SingletonInjectorProvider(provider)

        ##

        binding = InjectorBinding(key, provider)

        ##

        return binding


###
# injector


class _Injector(Injector):
    def __init__(self, bs: InjectorBindings, p: ta.Optional[Injector] = None) -> None:
        super().__init__()

        self._bs = check_isinstance(bs, InjectorBindings)
        self._p: ta.Optional[Injector] = check_isinstance(p, (Injector, type(None)))

        self._pfm = {k: v.provider_fn() for k, v in build_injector_provider_map(bs).items()}

    def try_provide(self, key: ta.Any) -> Maybe[ta.Any]:
        key = as_injector_key(key)

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
        raise UnboundInjectorKeyError(key)

    def provide_kwargs(self, obj: ta.Any) -> ta.Mapping[str, ta.Any]:
        kt = build_injection_kwargs_target(obj)
        ret: ta.Dict[str, ta.Any] = {}
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


def create_injector(bs: InjectorBindings, p: ta.Optional[Injector] = None) -> Injector:
    return _Injector(bs, p)


###
# injection helpers


class Injection:
    def __new__(cls, *args, **kwargs):  # noqa
        raise TypeError

    # keys

    @classmethod
    def as_key(cls, o: ta.Any) -> InjectorKey:
        return as_injector_key(o)

    @classmethod
    def array(cls, o: ta.Any) -> InjectorKey:
        return dc.replace(as_injector_key(o), array=True)

    @classmethod
    def tag(cls, o: ta.Any, t: ta.Any) -> InjectorKey:
        return dc.replace(as_injector_key(o), tag=t)

    # bindings

    @classmethod
    def as_bindings(cls, *vs: ta.Any) -> InjectorBindings:
        return as_injector_bindings(*vs)

    @classmethod
    def override(cls, p: InjectorBindings, *a: ta.Any) -> InjectorBindings:
        return injector_override(p, *a)

    # binder

    @classmethod
    def bind(
            cls,
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
    ) -> InjectorBinding:
        return InjectorBinder.bind(
            obj,

            key=key,
            tag=tag,
            array=array,

            to_fn=to_fn,
            to_ctor=to_ctor,
            to_const=to_const,
            to_key=to_key,

            singleton=singleton,
        )

    # injector

    @classmethod
    def create_injector(cls, bs: InjectorBindings, p: ta.Optional[Injector] = None) -> Injector:
        return create_injector(bs, p)


inj = Injection
