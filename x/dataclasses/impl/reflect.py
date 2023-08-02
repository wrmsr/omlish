import dataclasses as dc
import sys
import typing as ta

from omlish import cached
from omlish import check

from .internals import Params
from .metadata import Metadata
from .metadata import get_metadata
from .params import Params12
from .params import get_params


IS_12 = sys.version_info[1] >= 12


TypeT = ta.TypeVar('TypeT', bound=type, covariant=True)


class ClassInfo(ta.Generic[TypeT]):

    def __init__(self, cls: ta.Type[TypeT]) -> None:
        check.isinstance(cls, type)
        check.arg(dc.is_dataclass(cls))
        super().__init__()
        self._cls = cls

    @property
    def cls(self) -> TypeT:
        return self._cls

    @cached.property
    def metadata(self) -> Metadata:
        return get_metadata(self._cls)

    @cached.property
    def params(self) -> Params:
        return get_params(self._cls)

    @cached.property
    def params12(self) -> Params12:
        if IS_12:
            return Params12(
                match_args=(p := self.params).match_args,
                kw_only=p.kw_only,
                slots=p.slots,
                weakref_slot=p.weakref_slot,
            )
        elif (md_p12 := self.metadata.get(Params12)) is not None:
            return md_p12
        else:
            return Params12()
