import typing as ta

from ..errors import ReflectionTypeError
from .expandtype import expand_type
from .types import Type
from .types import TypeVarId
from .types import TypeVarLikeType


SubstitutionKey: ta.TypeAlias = TypeVarId | TypeVarLikeType
SubstitutionMap: ta.TypeAlias = ta.Mapping[SubstitutionKey, Type]
SubstitutionInputMap: ta.TypeAlias = ta.Mapping[ta.Any, ta.Any]


##


def substitute_type(typ: Type, replacements: SubstitutionInputMap) -> Type:
    return expand_type(typ, _validate_replacements(replacements))


def substitute_types(typs: ta.Sequence[Type], replacements: SubstitutionInputMap) -> list[Type]:
    env = _validate_replacements(replacements)
    return [expand_type(typ, env) for typ in typs]


def _validate_replacements(replacements: SubstitutionInputMap) -> SubstitutionMap:
    validated: dict[SubstitutionKey, Type] = {}
    for key, value in replacements.items():
        if not isinstance(key, (TypeVarId, TypeVarLikeType)):
            raise ReflectionTypeError(f'Unsupported substitution key: {key!r}')
        if not isinstance(value, Type):
            raise ReflectionTypeError(f'Unsupported substitution value: {value!r}')
        validated[key] = value
    return validated
