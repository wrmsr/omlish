import abc
import collections
import typing as ta

from ... import lang
from .api import dataclass
from .api import field  # noqa
from .params import MetaclassParams
from .params import get_metaclass_params


def confer_kwargs(
        bases: ta.Sequence[type],
        kwargs: ta.Mapping[str, ta.Any],
) -> dict[str, ta.Any]:
    out: dict[str, ta.Any] = {}
    for base in bases:
        if not (bmp := get_metaclass_params(base)).confer:
            continue
        for ck in bmp.confer:
            if ck == 'frozen':
                raise NotImplementedError
            elif ck == 'confer':
                raise NotImplementedError
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
            **kwargs
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
            metadata = collections.ChainMap(mmd, metadata)  # type: ignore
        else:
            metadata = mmd

        return dataclass(cls, metadata=metadata, **nkw)


# @ta.dataclass_transform(field_specifiers=(field,))  # FIXME: ctor
class Data(metaclass=DataMeta):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __post_init__(self, *args, **kwargs) -> None:
        try:
            spi = super().__post_init__  # type: ignore  # noqa
        except AttributeError:
            if args or kwargs:
                raise TypeError(args, kwargs)
        else:
            spi(*args, **kwargs)


class Frozen(Data, frozen=True, confer=frozenset(['frozen', 'confer'])):
    pass
