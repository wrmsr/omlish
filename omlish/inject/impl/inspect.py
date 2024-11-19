"""
TODO:
 - cache kwarg_keys
 - tag annotations? x: ta.Annotated[int, inj.Tag('foo')]
 - tag decorator - @inj.tag(x='foo')
 - *unpack optional here*
"""
import dataclasses as dc
import inspect
import typing as ta
import weakref

from ... import reflect as rfl
from ..exceptions import ConflictingKeyError
from ..inspect import Kwarg
from ..inspect import KwargsTarget
from ..keys import Key
from ..keys import as_key
from ..types import Tag


T = ta.TypeVar('T')
P = ta.ParamSpec('P')
R = ta.TypeVar('R')


##


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


##


_TAGS: ta.MutableMapping[ta.Any, dict[str, ta.Any]] = weakref.WeakKeyDictionary()


def tag(obj: T, **kwargs: ta.Any) -> T:
    for v in kwargs.values():
        if isinstance(v, Tag):
            raise TypeError(v)
    _TAGS.setdefault(obj, {}).update(**kwargs)
    return obj


def tags(**kwargs: ta.Any) -> ta.Callable[[ta.Callable[P, R]], ta.Callable[P, R]]:
    def inner(obj):
        _TAGS[obj] = kwargs
        return obj
    return inner


##


def build_kwargs_target(
        obj: ta.Any,
        *,
        skip_args: int = 0,
        skip_kwargs: ta.Iterable[ta.Any] | None = None,
        raw_optional: bool = False,
) -> KwargsTarget:
    sig = signature(obj)
    tags = _TAGS.get(obj)

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
                rf.is_optional
        ):
            ann = rf.without_none()

        rty = rfl.type_(ann)

        tag = None
        if isinstance(rty, rfl.Annotated):
            for e in rty.md:
                if isinstance(e, Tag):
                    tag = e.tag
                    break

        k: Key = Key(rfl.strip_annotations(rty), tag=tag)
        if tags is not None and (pt := tags.get(p.name)) is not None:
            k = dc.replace(k, tag=pt)

        if k in seen:
            raise ConflictingKeyError(k)
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
