import dataclasses as dc
import reprlib
import types
import typing as ta

from ...errors import FieldFnValidationError
from ...errors import FieldTypeValidationError
from ...errors import FnValidationError
from .idents import IDENT_PREFIX


##


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
    (ISINSTANCE_GLOBAL := FnGlobal(IDENT_PREFIX + 'isinstance')): FnGlobalValue(isinstance, 'isinstance'),
    (NONE_GLOBAL := FnGlobal(IDENT_PREFIX + 'None')): FnGlobalValue(None, 'None'),
    (PROPERTY_GLOBAL := FnGlobal(IDENT_PREFIX + 'property')): FnGlobalValue(property, 'property'),
    (TYPE_ERROR_GLOBAL := FnGlobal(IDENT_PREFIX + 'TypeError')): FnGlobalValue(TypeError, 'TypeError'),

    (OBJECT_SETATTR_GLOBAL := FnGlobal(IDENT_PREFIX + 'object_setattr')): FnGlobalValue(
        object.__setattr__,
        'object.__setattr__',
    ),

    (FROZEN_INSTANCE_ERROR_GLOBAL := FnGlobal(IDENT_PREFIX + 'FrozenInstanceError')): FnGlobalValue(
        dc.FrozenInstanceError,
        'dataclasses.FrozenInstanceError',
    ),
    (HAS_DEFAULT_FACTORY_GLOBAL := FnGlobal(IDENT_PREFIX + 'HAS_DEFAULT_FACTORY')): FnGlobalValue(
        dc._HAS_DEFAULT_FACTORY,  # type: ignore[attr-defined]  # noqa
        'dataclasses._HAS_DEFAULT_FACTORY',
    ),
    (MISSING_GLOBAL := FnGlobal(IDENT_PREFIX + 'MISSING')): FnGlobalValue(
        dc.MISSING,  # noqa
        'dataclasses.MISSING',
    ),

    (REPRLIB_RECURSIVE_REPR_GLOBAL := FnGlobal(IDENT_PREFIX + '_recursive_repr')): FnGlobalValue(
        reprlib.recursive_repr,
        'reprlib.recursive_repr',
    ),

    (FUNCTION_TYPE_GLOBAL := FnGlobal(IDENT_PREFIX + 'FunctionType')): FnGlobalValue(
        types.FunctionType,
        'types.FunctionType',
    ),

    (FIELD_FN_VALIDATION_ERROR_GLOBAL := FnGlobal(IDENT_PREFIX + 'FieldFnValidationError')): FnGlobalValue(
        FieldFnValidationError,
        '.errors.FieldFnValidationError',
    ),
    (FIELD_TYPE_VALIDATION_ERROR_GLOBAL := FnGlobal(IDENT_PREFIX + 'FieldTypeValidationError')): FnGlobalValue(
        FieldTypeValidationError,
        '.errors.FieldTypeValidationError',
    ),
    (FN_VALIDATION_ERROR_GLOBAL := FnGlobal(IDENT_PREFIX + 'FnValidationError')): FnGlobalValue(
        FnValidationError,
        '.errors.FnValidationError',
    ),
}


FN_GLOBAL_VALUES: ta.Mapping[str, ta.Any] = {
    k.ident: v.value
    for k, v in FN_GLOBALS.items()
}
