import dataclasses as dc
import typing as ta

from ..core.typekeys import TypeKey
from ..core.types import Type
from ..errors import ReflectionError
from ..errors import ReflectionTypeError
from ..reflect import DEFAULT_REFLECTOR
from ..reflect import TypeReflector
from .dataclasses import RuntimeDataclassInspection
from .dataclasses import inspect_dataclass
from .namedtuples import RuntimeNamedTupleInspection
from .namedtuples import inspect_namedtuple
from .namedtuples import is_namedtuple


RuntimeRecordKind: ta.TypeAlias = str


##


RUNTIME_RECORD_KIND_DATACLASS: ta.Final = 'dataclass'
RUNTIME_RECORD_KIND_NAMEDTUPLE: ta.Final = 'namedtuple'


@dc.dataclass(frozen=True)
class RuntimeRecordField:
    name: str
    typ: Type
    type_key: TypeKey
    structural_type_key: TypeKey
    annotation: object


@dc.dataclass(frozen=True)
class RuntimeRecordInspection:
    kind: RuntimeRecordKind
    origin: type
    fields: tuple[RuntimeRecordField, ...]
    fields_by_name: dict[str, RuntimeRecordField]


##


def _get_reflector(reflector: TypeReflector | None) -> TypeReflector:
    return DEFAULT_REFLECTOR if reflector is None else reflector


def _get_origin(obj: object) -> object:
    origin = ta.get_origin(obj)
    if origin is None:
        return obj
    return origin


def _from_dataclass(inspection: RuntimeDataclassInspection) -> RuntimeRecordInspection:
    fields = tuple(
        RuntimeRecordField(
            field.name,
            field.replaced_type,
            inspection.field_type_keys[field.name],
            inspection.field_structural_type_keys[field.name],
            inspection.field_annotations[field.name],
        )
        for field in inspection.fields
    )
    return RuntimeRecordInspection(
        RUNTIME_RECORD_KIND_DATACLASS,
        inspection.origin,
        fields,
        {field.name: field for field in fields},
    )


def _from_namedtuple(inspection: RuntimeNamedTupleInspection) -> RuntimeRecordInspection:
    fields = tuple(
        RuntimeRecordField(
            field.name,
            field.replaced_type,
            inspection.field_type_keys[field.name],
            inspection.field_structural_type_keys[field.name],
            inspection.field_annotations[field.name],
        )
        for field in inspection.fields
    )
    return RuntimeRecordInspection(
        RUNTIME_RECORD_KIND_NAMEDTUPLE,
        inspection.origin,
        fields,
        {field.name: field for field in fields},
    )


def inspect_record(
        obj: object,
        reflector: TypeReflector | None = None,
) -> RuntimeRecordInspection:
    rt_reflector = _get_reflector(reflector)
    return ta.cast(RuntimeRecordInspection, rt_reflector.cached_inspection(
        'record',
        obj,
        lambda: _inspect_record_uncached(obj, rt_reflector),
    ))


def _inspect_record_uncached(
        obj: object,
        rt_reflector: TypeReflector,
) -> RuntimeRecordInspection:
    origin = _get_origin(obj)

    if isinstance(origin, type) and dc.is_dataclass(origin):
        return _from_dataclass(inspect_dataclass(obj, rt_reflector))

    if is_namedtuple(origin):
        return _from_namedtuple(inspect_namedtuple(obj, rt_reflector))

    raise ReflectionTypeError(f'Unsupported record source: {obj!r}')


def inspect_record_or_none(
        obj: object,
        reflector: TypeReflector | None = None,
) -> RuntimeRecordInspection | None:
    try:
        return inspect_record(obj, reflector)
    except ReflectionError:
        return None
