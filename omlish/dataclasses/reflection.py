import dataclasses as dc
import typing as ta

from .. import lang
from ._internals import STD_PARAMS_ATTR
from ._internals import StdFieldType
from ._internals import std_field_type
from .impl.api.classes.conversion import std_params_to_class_spec
from .impl.api.classes.metadata import extract_cls_metadata
from .impl.api.classes.params import get_class_spec
from .impl.api.fields.conversion import std_field_to_field_spec
from .impl.concerns.fields import InitFields
from .impl.concerns.fields import calc_init_fields
from .inspect import FieldsInspection
from .inspect import inspect_fields
from .specs import ClassSpec


##


class ClassReflection:
    def __init__(self, cls: type) -> None:
        super().__init__()

        self._cls = cls

    @property
    def cls(self) -> type:
        return self._cls

    #

    @lang.cached_property
    def spec(self) -> ClassSpec:
        if (cs := get_class_spec(self._cls)) is not None:
            return cs

        try:
            p = getattr(self._cls, STD_PARAMS_ATTR)
        except AttributeError:
            raise TypeError(self._cls) from None

        # This class was not constructed as one of our dataclasses, so surface no additional functionality even if
        # present as extra_params or such.
        fsl = [
            std_field_to_field_spec(
                f,
                ignore_metadata=True,
                ignore_extra_params=True,
            )
            for f in dc.fields(self._cls)  # noqa
        ]

        cmd = extract_cls_metadata(self._cls, deep=True)

        cs = std_params_to_class_spec(
            p,
            fsl,
            metadata=cmd.user_metadata or None,
        )

        return cs

    #

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

    #

    @lang.cached_property
    def type_hints(self) -> ta.Mapping[str, ta.Any]:
        return ta.get_type_hints(self._cls)

    @lang.cached_property
    def field_annotations(self) -> ta.Mapping[str, ta.Any]:
        return {
            f: self.type_hints[f]
            for f in self.fields
            if f in self.type_hints
        }


def reflect(cls: type) -> ClassReflection:
    return ClassReflection(cls)
