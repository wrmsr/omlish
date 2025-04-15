import dataclasses as dc
import reprlib
import types
import typing as ta

from ..errors import FieldFnValidationError
from ..errors import FieldTypeValidationError
from ..errors import FnValidationError


##


IDENT_PREFIX = '__dataclass__'

CLS_IDENT = IDENT_PREFIX + 'cls'
SELF_IDENT = IDENT_PREFIX + 'self'
SELF_DICT_IDENT = IDENT_PREFIX + 'self_dict'
VALUE_IDENT = IDENT_PREFIX + 'value'


#


class FnGlobal(ta.NamedTuple):
    ident: str


class FnGlobalValue(ta.NamedTuple):
    value: ta.Any
    src: str  # Leading '.' denotes a dataclasses-internal symbol


FN_GLOBAL_IMPORTS: ta.Mapping[str, types.ModuleType] = {
    'dataclasses': dc,
    'reprlib': reprlib,
    'types': types,
}


FN_GLOBALS: ta.Mapping[FnGlobal, FnGlobalValue] = {
    FnGlobal(ISINSTANCE_IDENT := IDENT_PREFIX + 'isinstance'): FnGlobalValue(isinstance, 'isinstance'),
    FnGlobal(NONE_IDENT := IDENT_PREFIX + 'None'): FnGlobalValue(None, 'None'),
    FnGlobal(PROPERTY_IDENT := IDENT_PREFIX + 'property'): FnGlobalValue(property, 'property'),
    FnGlobal(TYPE_ERROR_IDENT := IDENT_PREFIX + 'TypeError'): FnGlobalValue(TypeError, 'TypeError'),

    FnGlobal(OBJECT_SETATTR_IDENT := IDENT_PREFIX + 'object_setattr'): FnGlobalValue(
        object.__setattr__,
        'object.__setattr__',
    ),

    FnGlobal(FROZEN_INSTANCE_ERROR_IDENT := IDENT_PREFIX + 'FrozenInstanceError'): FnGlobalValue(
        dc.FrozenInstanceError,
        'dataclasses.FrozenInstanceError',
    ),
    FnGlobal(HAS_DEFAULT_FACTORY_IDENT := IDENT_PREFIX + 'HAS_DEFAULT_FACTORY'): FnGlobalValue(
        dc._HAS_DEFAULT_FACTORY,  # type: ignore[attr-defined]  # noqa
        'dataclasses._HAS_DEFAULT_FACTORY',
    ),
    FnGlobal(MISSING_IDENT := IDENT_PREFIX + 'MISSING'): FnGlobalValue(
        dc.MISSING,  # noqa
        'dataclasses.MISSING',
    ),

    FnGlobal(REPRLIB_RECURSIVE_REPR_IDENT := IDENT_PREFIX + '_recursive_repr'): FnGlobalValue(
        reprlib.recursive_repr,
        'reprlib.recursive_repr',
    ),

    FnGlobal(FUNCTION_TYPE_IDENT := IDENT_PREFIX + 'FunctionType'): FnGlobalValue(
        types.FunctionType,
        'types.FunctionType',
    ),

    FnGlobal(FIELD_FN_VALIDATION_ERROR_IDENT := IDENT_PREFIX + 'FieldFnValidationError'): FnGlobalValue(
        FieldFnValidationError,
        '.errors.FieldFnValidationError',
    ),
    FnGlobal(FIELD_TYPE_VALIDATION_ERROR_IDENT := IDENT_PREFIX + 'FieldTypeValidationError'): FnGlobalValue(
        FieldTypeValidationError,
        '.errors.FieldTypeValidationError',
    ),
    FnGlobal(FN_VALIDATION_ERROR_IDENT := IDENT_PREFIX + 'FnValidationError'): FnGlobalValue(
        FnValidationError,
        '.errors.FnValidationError',
    ),
}


FN_GLOBAL_VALUES: ta.Mapping[str, ta.Any] = {
    k.ident: v.value
    for k, v in FN_GLOBALS.items()
}
