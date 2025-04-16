import dataclasses as dc
import typing as ta

from .. import check
from .. import lang
from .api.classes.conversion import std_params_to_class_spec
from .api.classes.params import get_class_spec
from .api.fields.conversion import std_field_to_field_spec
from .concerns.fields import InitFields
from .concerns.fields import calc_init_fields
from .inspect import FieldsInspection
from .inspect import inspect_fields
from .internals import StdFieldType
from .internals import std_field_type
from .specs import ClassSpec


##


class ClassReflection:
    def __init__(self, cls: type) -> None:
        super().__init__()

        self._cls = cls

    @property
    def cls(self) -> type:
        return self._cls

    @lang.cached_property
    def spec(self) -> ClassSpec:
        if (cs := get_class_spec(self._cls)) is not None:
            return cs
        raise NotImplementedError

    @lang.cached_property
    def fields_inspection(self) -> FieldsInspection:
        return inspect_fields(self._cls)

    @lang.cached_property
    def init_fields(self) -> InitFields:
        return calc_init_fields(
            self.spec.fields,
            reorder=self.spec.reorder,
            class_kw_only=self.spec.kw_only,
        )

    @lang.cached_property
    def fields(self) -> ta.Mapping[str, dc.Field]:
        return {f.name: f for f in dc.fields(self._cls)}  # noqa

    @lang.cached_property
    def instance_fields(self) -> ta.Sequence[dc.Field]:
        return [f for f in self.fields.values() if std_field_type(f) is StdFieldType.INSTANCE]


def reflect(cls: type) -> ClassReflection:
    return ClassReflection(cls)
