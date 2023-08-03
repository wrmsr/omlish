import abc

from omlish import lang

from .classes import dataclass


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
        return dataclass(cls, **kwargs)


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
