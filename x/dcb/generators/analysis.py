import typing as ta

from omlish import cached

from ..specs import ClassSpec
from ..specs import FieldSpec
from ..specs import FieldType


##


class ClassAnalysis:
    def __init__(self, cls: type, cs: ClassSpec) -> None:
        super().__init__()

        self._cls = cls
        self._cs = cs

    @property
    def cls(self) -> type:
        return self._cls

    @property
    def cs(self) -> ClassSpec:
        return self._cs

    #

    @cached.property
    def instance_fields(self) -> ta.Sequence[FieldSpec]:
        return [f for f in self._cs.fields if f.field_type is FieldType.INSTANCE]
