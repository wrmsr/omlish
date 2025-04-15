import dataclasses as dc
import typing as ta

from omlish import check
from omlish import lang

from ...specs import FieldSpec


##


class _ExtraParams(lang.Marker):
    pass


def extra_field_params(**kwargs) -> ta.Mapping[ta.Any, ta.Any]:
    return {_ExtraParams: kwargs}


##


def get_field_spec(f: dc.Field) -> FieldSpec:
    return check.isinstance(f.metadata[FieldSpec], FieldSpec)
