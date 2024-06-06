"""
TODO:
 - cache kwarg_keys
 - tag annotations
"""
import inspect
import typing as ta
import weakref

from .exceptions import DuplicateKeyException
from .keys import as_key
from .types import Key


_signature_cache: ta.MutableMapping[ta.Any, inspect.Signature] = weakref.WeakKeyDictionary()


def signature(obj: ta.Any) -> inspect.Signature:
    try:
        return _signature_cache[obj]
    except TypeError:
        return inspect.signature(obj)
    except KeyError:
        pass
    sig = inspect.signature(obj)
    _signature_cache[obj] = sig
    return sig


class Kwarg(ta.NamedTuple):
    key: Key
    has_default: bool


class Target(ta.NamedTuple):
    obj: ta.Any
    kwargs: ta.Mapping[str, Kwarg]


def build_kwarg_keys(
        obj: ta.Any,
        *,
        skip_args: int = 0,
        skip_kwargs: ta.Optional[ta.Iterable[ta.Any]] = None,
) -> ta.Mapping[str, Key]:
    sig = signature(obj)

    seen: set[Key] = set(map(as_key, skip_kwargs)) if skip_kwargs is not None else set()
    kd: dict[str, Key] = {}
    for p in list(sig.parameters.values())[skip_args:]:
        k = as_key(p.annotation)

        if k in seen:
            raise DuplicateKeyException(k)
        seen.add(k)

        if p.kind not in (inspect.Parameter.POSITIONAL_OR_KEYWORD, inspect.Parameter.KEYWORD_ONLY):
            raise TypeError(sig)
        kd[p.name] = k

    return kd
