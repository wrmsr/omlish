import inspect
import typing as ta

from .. import check
from .bindings import build_provider_map
from .exceptions import DuplicateKeyException
from .exceptions import UnboundKeyException
from .inspect import signature
from .keys import as_key
from .types import Bindings
from .types import Injector
from .types import Key


class _Injector(Injector):
    def __init__(self, bs: Bindings, p: ta.Optional['Injector'] = None) -> None:
        super().__init__()

        self._bs = check.isinstance(bs, Bindings)
        self._p = check.isinstance(p, (Injector, None))

        self._pfm = {k: v.provider_fn() for k, v in build_provider_map(bs).items()}

    def try_provide(self, key: ta.Any) -> ta.Optional[ta.Any]:
        key = as_key(key)

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
            k = as_key(p.annotation)

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
