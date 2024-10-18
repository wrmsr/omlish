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
from .api import dataclass
from .api import field  # noqa
from .params import MetaclassParams
from .params import get_metaclass_params
from .params import get_params
from .params import get_params_extras


T = ta.TypeVar('T')


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

            if ck in (
                    'frozen',
                    'kw_only',
            ):
                confer_kwarg(out, ck, getattr(get_params(base), ck))

            elif ck in (
                    'cache_hash',
                    'generic_init',
                    'reorder',
            ):
                confer_kwarg(out, ck, getattr(get_params_extras(base), ck))

            elif ck in (
                    'confer',
            ):
                confer_kwarg(out, ck, getattr(bmp, ck))

            else:
                raise KeyError(ck)

    return out


class DataMeta(abc.ABCMeta):
    def __new__(
            mcls,
            name,
            bases,
            namespace,
            *,

            # confer=frozenset(),

            metadata=None,
            **kwargs,
    ):
        cls = lang.super_meta(
            super(),
            mcls,
            name,
            bases,
            namespace,
        )

        ckw = confer_kwargs(bases, kwargs)
        nkw = {**kwargs, **ckw}

        mcp = MetaclassParams(
            confer=nkw.pop('confer', frozenset()),
        )

        mmd = {
            MetaclassParams: mcp,
        }
        if metadata is not None:
            metadata = collections.ChainMap(mmd, metadata)
        else:
            metadata = mmd

        return dataclass(cls, metadata=metadata, **nkw)


# @ta.dataclass_transform(field_specifiers=(field,))  # FIXME: ctor
class Data(
    eq=False,
    order=False,
    metaclass=DataMeta,
):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

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
        'frozen',
        'cache_hash',
        'confer',
    ]),
):
    pass


class Box(
    Frozen,
    ta.Generic[T],
    generic_init=True,
    confer=frozenset([
        'frozen',
        'cache_hash',
        'generic_init',
        'confer',
    ]),
):
    v: T
