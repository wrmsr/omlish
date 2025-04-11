import dataclasses as dc
import types
import typing as ta

from ..exceptions import FieldFnValidationError
from ..exceptions import FieldTypeValidationError
from ..exceptions import FnValidationError


##


IDENT_PREFIX = '__dataclass__'

CLS_IDENT = IDENT_PREFIX + 'cls'
SELF_IDENT = IDENT_PREFIX + 'self'
SELF_DICT_IDENT = IDENT_PREFIX + 'self_dict'
VALUE_IDENT = IDENT_PREFIX + 'value'


#


class FnGlobal(ta.NamedTuple):
    value: ta.Any
    src: str  # Leading '.' denotes a dataclasses-internal symbol


FN_GLOBAL_IMPORTS: ta.Mapping[str, types.ModuleType] = {
    'dataclasses': dc,
    'types': types,
}


FN_GLOBALS: ta.Mapping[str, FnGlobal] = {
    (ISINSTANCE_IDENT := IDENT_PREFIX + 'isinstance'): FnGlobal(isinstance, 'isinstance'),
    (NONE_IDENT := IDENT_PREFIX + 'None'): FnGlobal(None, 'None'),
    (PROPERTY_IDENT := IDENT_PREFIX + 'property'): FnGlobal(property, 'property'),

    (OBJECT_SETATTR_IDENT := IDENT_PREFIX + 'object_setattr'): FnGlobal(
        object.__setattr__,
        'object.__setattr__',
    ),

    (FROZEN_INSTANCE_ERROR_IDENT := IDENT_PREFIX + 'FrozenInstanceError'): FnGlobal(
        dc.FrozenInstanceError,
        'dataclasses.FrozenInstanceError',
    ),
    (HAS_DEFAULT_FACTORY_IDENT := IDENT_PREFIX + 'HAS_DEFAULT_FACTORY'): FnGlobal(
        dc._HAS_DEFAULT_FACTORY,  # type: ignore[attr-defined]  # noqa
        'dataclasses._HAS_DEFAULT_FACTORY',
    ),
    (MISSING_IDENT := IDENT_PREFIX + 'MISSING'): FnGlobal(
        dc.MISSING,  # noqa
        'dataclasses.MISSING',
    ),

    (FUNCTION_TYPE_IDENT := IDENT_PREFIX + 'FunctionType'): FnGlobal(
        types.FunctionType,
        'types.FunctionType',
    ),

    (FIELD_FN_VALIDATION_ERROR_IDENT := IDENT_PREFIX + 'FieldFnValidationError'): FnGlobal(
        FieldFnValidationError,
        '.exceptions.FieldFnValidationError',
    ),
    (FIELD_TYPE_VALIDATION_ERROR_IDENT := IDENT_PREFIX + 'FieldTypeValidationError'): FnGlobal(
        FieldTypeValidationError,
        '.exceptions.FieldTypeValidationError',
    ),
    (FN_VALIDATION_ERROR_IDENT := IDENT_PREFIX + 'FnValidationError'): FnGlobal(
        FnValidationError,
        '.exceptions.FnValidationError',
    ),
}


FN_GLOBAL_VALUES: ta.Mapping[str, ta.Any] = {
    k: v.value
    for k, v in FN_GLOBALS.items()
}
