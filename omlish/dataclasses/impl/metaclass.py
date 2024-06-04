import abc
import typing as ta

from ... import lang
from .api import field  # noqa

if ta.TYPE_CHECKING:
    from . import api
else:
    api = lang.proxy_import('.api', __package__)


class DataMeta(abc.ABCMeta):
    def __new__(
            mcls,
            name,
            bases,
            namespace,
            **kwargs
    ):
        cls = lang.super_meta(
            super(),
            mcls,
            name,
            bases,
            namespace,
        )
        return api.dataclass(cls, **kwargs)


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
