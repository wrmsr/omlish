"""
TODO:
 - cache kwarg_keys
 - tag annotations
"""
import inspect
import typing as ta
import weakref

from omlish.lite.reflect import get_optional_alias_arg
from omlish.lite.reflect import is_optional_alias

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
