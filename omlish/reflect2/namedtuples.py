# ruff: noqa: SLF001
import dataclasses as dc
import typing as ta

from .core.substitute import substitute_type
from .core.types import Instance
from .core.types import Type
from .core.types import TypeVarLikeType
from .errors import ReflectionTypeError
from .errors import UnsupportedTypeOperationError
from .globals import or_global_reflector
from .reflector import TypeReflector


##


@dc.dataclass(frozen=True)
class NamedtupleField:
    name: str
    raw_type: Type
    replaced_type: Type


@dc.dataclass(frozen=True)
class NamedtupleInspection:
    origin: type
    fields: tuple[NamedtupleField, ...]
    fields_by_name: ta.Mapping[str, NamedtupleField]


##


def _get_origin_namedtuple(obj: object) -> type:
    origin = ta.get_origin(obj)
    if origin is None:
        origin = obj

    if not isinstance(origin, type) or not is_namedtuple(origin):
        raise ReflectionTypeError(f'Unsupported namedtuple source: {obj!r}')

    return origin


def is_namedtuple(obj: object) -> bool:
    return (
        isinstance(obj, type) and
        issubclass(obj, tuple) and
        ta.NamedTuple in getattr(obj, '__orig_bases__', ()) and
        isinstance(getattr(obj, '_fields', None), tuple)
    )


def _get_namedtuple_annotations(origin: type) -> dict[str, object]:
    annotations = getattr(origin, '__annotations__', {})
    if not isinstance(annotations, dict):
        raise ReflectionTypeError(f'Unsupported namedtuple annotations for {origin!r}: {annotations!r}')
    return annotations


class NamedtupleInspector:
    def __init__(self, reflector: TypeReflector) -> None:
        super().__init__()

        self._reflector = reflector

    def _get_replacements(
            self,
            obj: object,
            origin: type,
    ) -> dict[TypeVarLikeType, Type]:
        instance = self._reflector.reflect_type(obj)
        if not isinstance(instance, Instance):
            raise ReflectionTypeError(f'Unsupported namedtuple reflected type: {instance!r}')

        origin_info = self._reflector.get_type_info(origin)
        if instance._type is not origin_info:
            raise UnsupportedTypeOperationError(f'Namedtuple origin mismatch: {instance!r} != {origin_info._fullname}')

        if not origin_info._type_vars:
            return {}

        if len(origin_info.type_vars) != len(instance._args):
            raise UnsupportedTypeOperationError(
                f'Cannot replace namedtuple field type with mismatched args: {instance!r}',
            )

        return dict(zip(origin_info.type_vars, instance._args))

    def inspect_namedtuple(self, obj: object) -> NamedtupleInspection:
        origin = _get_origin_namedtuple(obj)
        annotations = _get_namedtuple_annotations(origin)
        replacements = self._get_replacements(obj, origin)

        ret: list[NamedtupleField] = []
        for name in getattr(origin, '_fields'):
            try:
                annotation = annotations[name]
            except KeyError:
                raise ReflectionTypeError(f'Missing namedtuple field annotation: {origin!r}.{name}') from None

            raw_type = self._reflector.reflect_type(annotation)
            replaced_type = (
                substitute_type(raw_type, replacements)
                if replacements else raw_type
            )
            ret.append(NamedtupleField(name, raw_type, replaced_type))

        fields = tuple(ret)
        fields_by_name = {
            field.name: field
            for field in fields
        }
        return NamedtupleInspection(
            origin,
            fields,
            fields_by_name,
        )


def inspect_namedtuple(obj: object, *, reflector: TypeReflector | None = None) -> NamedtupleInspection:
    return NamedtupleInspector(or_global_reflector(reflector)).inspect_namedtuple(obj)
