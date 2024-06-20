"""
TODO:
 - cache kwarg_keys
 - tag annotations? x: ta.Annotated[int, inj.Tag('foo')]
 - tag decorator - @inj.tag(x='foo')
 - *unpack optional here*
"""
import inspect
import types
import typing as ta
import weakref

from ... import reflect as rfl
from ..exceptions import DuplicateKeyException
from ..inspect import Kwarg
from ..inspect import KwargsTarget
from ..keys import Key
from ..keys import as_key
from ..keys import tag


P = ta.ParamSpec('P')
R = ta.TypeVar('R')


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


_tags: ta.MutableMapping[ta.Any, dict[str, ta.Any]] = weakref.WeakKeyDictionary()


def tags(**kwargs: ta.Any) -> ta.Callable[[ta.Callable[P, R]], ta.Callable[P, R]]:
    def inner(obj):
        _tags[obj] = kwargs
        return obj
    return inner


def build_kwargs_target(
        obj: ta.Any,
        *,
        skip_args: int = 0,
        skip_kwargs: ta.Optional[ta.Iterable[ta.Any]] = None,
        raw_optional: bool = False,
) -> KwargsTarget:
    sig = signature(obj)
    tags = _tags.get(obj)

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
                isinstance(rf := rfl.type_(ann), rfl.Union) and
                len(rf.args) == 2   # noqa
                and types.NoneType in rf.args
        ):
            [ann] = [a for a in rf.args if a is not types.NoneType]

        k = as_key(ann)
        if tags is not None and (pt := tags.get(p.name)) is not None:
            k = tag(k, pt)

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
