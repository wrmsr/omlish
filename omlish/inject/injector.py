import inspect
import typing as ta

from .. import check
from .. import lang
from .exceptions import DuplicateKeyException
from .exceptions import UnboundKeyException
from .inspect import signature
from .providers import ConstProvider
from .providers import Provider
from .types import Binder
from .types import Binding
from .types import Bindings
from .types import Injector
from .types import Key
from .types import _BindingGen
from .types import _ProviderGen


def _as_key(o: ta.Any) -> Key:
    if isinstance(o, Key):
        return o
    if isinstance(o, type):
        return Key(o)
    raise TypeError(o)


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


class _Injector(Injector):
    def __init__(self, bs: Bindings, p: ta.Optional['Injector'] = None) -> None:
        super().__init__()

        self._bs = bs
        self._p = check.isinstance(p, (Injector, type(None)))

        self._pfm = {k: v.provider_fn() for k, v in _build_provider_map(bs).items()}

    def try_provide(self, key: ta.Any) -> ta.Optional[ta.Any]:
        check.isinstance(key, Key)
        fn = self._pfm.get(key)
        if fn is not None:
            return fn(self)
        if self._p is not None:
            pv = self._p.try_provide(key)
            if pv is not None:
                return None
        return None

    def provide(self, key: ta.Any) -> ta.Any:
        v = self.try_provide(key)
        if v is not None:
            return v
        raise UnboundKeyException(key)

    def provide_kwargs(self, obj: ta.Any) -> ta.Mapping[str, ta.Any]:
        sig = signature(obj)

        seen: ta.Set[Key] = set()
        kd: ta.Dict[str, Key] = {}
        for p in sig.parameters.values():
            k = _as_key(p.annotation)

            if k in seen:
                raise DuplicateKeyException(k)
            seen.add(k)

            if p.kind not in (inspect.Parameter.POSITIONAL_OR_KEYWORD, inspect.Parameter.KEYWORD_ONLY):
                raise TypeError(sig)
            kd[p.name] = k

        ret: ta.Dict[str, ta.Any] = {}
        for n, k in kd.items():
            ret[n] = self.provide(k)
        return ret

    def inject(self, obj: ta.Any) -> ta.Any:
        kws = self.provide_kwargs(obj)
        return obj(**kws)


def create_injector(bs: Bindings, p: ta.Optional['Injector'] = None) -> Injector:
    return _Injector(bs, p)
