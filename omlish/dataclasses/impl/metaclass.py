"""
TODO:
 - Rewrite lol
 - Enum - enforce Abstract or Final
"""
import abc
import collections
import dataclasses as dc
import typing as ta

from ... import lang
from .api import MISSING
from .api import dataclass
from .api import field  # noqa
from .params import MetaclassParams
from .params import get_metaclass_params
from .params import get_params
from .params import get_params_extras


T = ta.TypeVar('T')


##


_CONFER_PARAMS: tuple[str, ...] = (
    'eq',
    'frozen',
    'kw_only',
)

_CONFER_PARAMS_EXTRAS: tuple[str, ...] = (
    'reorder',
    'cache_hash',
    'generic_init',
    'override',
)

_CONFER_METACLASS_PARAMS: tuple[str, ...] = (
    'confer',
    'final_subclasses',
    'abstract_immediate_subclasses',
)


def confer_kwarg(out: dict[str, ta.Any], k: str, v: ta.Any) -> None:
    if k in out:
        if out[k] != v:
            raise ValueError
    else:
        out[k] = v


def confer_kwargs(
        bases: ta.Sequence[type],
        kwargs: ta.Mapping[str, ta.Any],
) -> dict[str, ta.Any]:
    out: dict[str, ta.Any] = {}
    for base in bases:
        if not dc.is_dataclass(base):
            continue

        if not (bmp := get_metaclass_params(base)).confer:
            continue

        for ck in bmp.confer:
            if ck in kwargs:
                continue

            if ck in _CONFER_PARAMS:
                confer_kwarg(out, ck, getattr(get_params(base), ck))

            elif ck in _CONFER_PARAMS_EXTRAS:
                confer_kwarg(out, ck, getattr(get_params_extras(base), ck))

            elif ck in _CONFER_METACLASS_PARAMS:
                confer_kwarg(out, ck, getattr(bmp, ck))

            else:
                raise KeyError(ck)

    return out


##


class DataMeta(abc.ABCMeta):
    def __new__(
            mcls,
            name,
            bases,
            namespace,
            *,

            abstract=False,
            sealed=False,
            final=False,

            metadata=None,
            **kwargs,
    ):
        ckw = confer_kwargs(bases, kwargs)
        nkw = {**kwargs, **ckw}

        mcp = MetaclassParams(**{
            mpa: nkw.pop(mpa)
            for mpa in _CONFER_METACLASS_PARAMS
            if mpa in nkw
        })

        mmd = {
            MetaclassParams: mcp,
        }
        if metadata is not None:
            metadata = collections.ChainMap(mmd, metadata)
        else:
            metadata = mmd

        #

        xbs: list[type] = []

        if any(get_metaclass_params(b).abstract_immediate_subclasses for b in bases if dc.is_dataclass(b)):
            abstract = True

        final |= (mcp.final_subclasses and not abstract)

        if final and abstract:
            raise TypeError(f'Class cannot be abstract and final: {name!r}')

        if abstract:
            xbs.append(lang.Abstract)
        if sealed:
            xbs.append(lang.Sealed)
        if final:
            xbs.append(lang.Final)

        if xbs:
            if bases and bases[-1] is ta.Generic:
                bases = (*bases[:-1], *xbs, bases[-1])
            else:
                bases = (*bases, *xbs)
            if ob := namespace.get('__orig_bases__'):
                if getattr(ob[-1], '__origin__', None) is ta.Generic:
                    namespace['__orig_bases__'] = (*ob[:-1], *xbs, ob[-1])
                else:
                    namespace['__orig_bases__'] = (*ob, *xbs)

        #

        ofs: set[str] = set()
        if any(issubclass(b, lang.Abstract) for b in bases) and nkw.get('override'):
            ofs.update(a for a in namespace.get('__annotations__', []) if a not in namespace)
            namespace.update((a, MISSING) for a in ofs)

        #

        cls = lang.super_meta(
            super(),
            mcls,
            name,
            bases,
            namespace,
        )

        #

        for a in ofs:
            delattr(cls, a)

        #

        return dataclass(cls, metadata=metadata, **nkw)


##


# @ta.dataclass_transform(field_specifiers=(field,))  # FIXME: ctor
class Data(
    eq=False,
    order=False,
    confer=frozenset([
        'confer',
        'final_subclasses',
    ]),
    metaclass=DataMeta,
):
    def __init__(self, *args, **kwargs):
        # Typechecking barrier
        super().__init__(*args, **kwargs)

    def __init_subclass__(cls, **kwargs):
        # Typechecking barrier
        super().__init_subclass__(**kwargs)

    def __post_init__(self, *args, **kwargs) -> None:
        try:
            spi = super().__post_init__  # type: ignore  # noqa
        except AttributeError:
            if args or kwargs:
                raise TypeError(args, kwargs) from None
        else:
            spi(*args, **kwargs)


class Frozen(
    Data,
    frozen=True,
    eq=False,
    order=False,
    confer=frozenset([
        *get_metaclass_params(Data).confer,
        'frozen',
        'reorder',
        'cache_hash',
        'override',
    ]),
):
    pass


class Case(
    Frozen,
    abstract=True,
    override=True,
    final_subclasses=True,
    abstract_immediate_subclasses=True,
):
    pass


class Box(
    Frozen,
    ta.Generic[T],
    generic_init=True,
    confer=frozenset([
        *get_metaclass_params(Frozen).confer,
        'generic_init',
    ]),
):
    v: T
