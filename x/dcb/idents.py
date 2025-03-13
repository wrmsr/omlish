import dataclasses as dc
import types


IDENT_PREFIX = '__dataclass__'

CLS_IDENT = IDENT_PREFIX + 'cls'
SELF_IDENT = IDENT_PREFIX + 'self'
VALUE_IDENT = IDENT_PREFIX + 'value'

FN_GLOBALS = {
    (NONE_IDENT := IDENT_PREFIX + 'None'): None,
    (PROPERTY_IDENT := IDENT_PREFIX + 'property'): property,
    (TYPE_ERROR_IDENT := IDENT_PREFIX + 'TypeError'): TypeError,

    (OBJECT_SETATTR_IDENT := IDENT_PREFIX + 'object_setattr'): object.__setattr__,

    (FROZEN_INSTANCE_ERROR_IDENT := IDENT_PREFIX + 'FrozenInstanceError'): dc.FrozenInstanceError,

    (FUNCTION_TYPE_IDENT := IDENT_PREFIX + 'FunctionType'): types.FunctionType,
}
