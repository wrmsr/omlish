"""
TODO:
 - generics? injected Manifests / type contexts?
 - ta.Literal? support for simple scalars, enums
 - multidispatch? never solved..
  - just generic on tuple[A0, A1, ...]
"""
import inspect
import typing as ta

from .. import c3
from .. import check
from .. import reflect as rfl


T = ta.TypeVar('T')


##


def get_impl_func_cls_set(func: ta.Callable, *, arg_offset: int = 0) -> frozenset[type]:
    if not rfl.has_annotations(func):
        raise TypeError(f'Invalid impl func: {func!r}')

    def erase(a):
        if isinstance(a, rfl.Generic):
            return a.cls
        else:
            return check.isinstance(a, type)

    # Exclude 'return' to support difficult to handle return types - they are unimportant.
    th_dct = rfl.get_filtered_type_hints(func, exclude=['return'])

    ps = inspect.signature(func).parameters
    p = list(ps.values())[arg_offset]
    cls = th_dct[p.name]

    rty = rfl.type_(cls)
    if isinstance(rty, rfl.Union):
        ret = frozenset(erase(arg) for arg in rty.args)
    else:
        ret = frozenset([erase(rty)])

    return ret


##


def find_impl(cls: type, registry: ta.Mapping[type, T]) -> T | None:
    mro = c3.compose_mro(cls, registry.keys())

    match: type | None = None
    for t in mro:
        if match is not None:
            # If *match* is an implicit ABC but there is another unrelated, equally matching implicit ABC, refuse the
            # temptation to guess.
            if (
                    t in registry
                    and t not in cls.__mro__
                    and match not in cls.__mro__
                    and not issubclass(match, t)
            ):
                raise RuntimeError(f'Ambiguous dispatch: {match} or {t}')
            break

        if t in registry:
            match = t

    if match is None:
        return None
    return registry.get(match)
