import dataclasses as dc
import typing as ta

from omlish import cached
from omlish import check

from .internals import Params
from .metadata import Metadata
from .metadata import get_merged_metadata
from .params import Params12
from .params import ParamsExtras
from .params import get_params
from .params import get_params12
from .params import get_params_extras


TypeT = ta.TypeVar('TypeT', bound=type, covariant=True)


class ClassInfo(ta.Generic[TypeT]):

    def __init__(self, cls: ta.Type[TypeT]) -> None:
        check.isinstance(cls, type)
        check.arg(dc.is_dataclass(cls))
        super().__init__()
        self._cls = cls

    @property
    def cls(self) -> ta.Type[TypeT]:
        return self._cls

    @cached.property
    def params(self) -> Params:
        return get_params(self._cls)

    @cached.property
    def params12(self) -> Params12:
        return get_params12(self._cls)

    @cached.property
    def params_extras(self) -> ParamsExtras:
        return get_params_extras(self._cls)

    @cached.property
    def merged_metadata(self) -> Metadata:
        return get_merged_metadata(self._cls)


def reflect(obj: ta.Any) -> ClassInfo:
    cls = obj if isinstance(obj, type) else type(obj)
    return ClassInfo(cls)
