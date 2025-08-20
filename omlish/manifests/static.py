import abc
import typing as ta

from .. import dataclasses as dc
from .. import lang
from .base import ModAttrManifest


##


class StaticModAttrManifest(dc.Static, ModAttrManifest, abc.ABC):
    def __init_subclass__(cls, **kwargs: ta.Any) -> None:
        if (
                not (lang.is_abstract_class(cls) or abc.ABC in cls.__bases__) and
                'module' not in cls.__dict__
        ):
            setattr(cls, 'module', cls.__module__)

        super().__init_subclass__(**kwargs)
