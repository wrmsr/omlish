import abc
import collections

from ... import lang
from .api import dataclass
from .api import field  # noqa
from .params import MetaclassParams


class DataMeta(abc.ABCMeta):
    def __new__(
            mcls,
            name,
            bases,
            namespace,
            *,

            confer=frozenset(),

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

        mcp = MetaclassParams(
            confer=confer,
        )

        mmd = {
            MetaclassParams: mcp,
        }
        if metadata is not None:
            metadata = collections.ChainMap(mmd, metadata)  # type: ignore
        else:
            metadata = mmd

        return dataclass(cls, metadata=metadata, **kwargs)


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


class Frozen(Data, frozen=True, confer=frozenset(['frozen'])):
    pass
