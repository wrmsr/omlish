import dataclasses as dc

from .specs import ClassSpec
from .specs import FieldSpec
from .std import StdParams


##


def field_spec_to_std_field(fs: FieldSpec) -> dc.Field:
    raise NotImplementedError


def std_field_to_field_spec(f: dc.Field) -> FieldSpec:
    raise NotImplementedError


##


def class_spec_to_std_params(cs: ClassSpec) -> StdParams:
    raise NotImplementedError


def std_params_to_class_spec(p: StdParams) -> ClassSpec:
    raise NotImplementedError
