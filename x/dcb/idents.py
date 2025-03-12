import dataclasses as dc


IDENT_PREFIX = '__dataclass__'

CLS_IDENT = IDENT_PREFIX + 'cls'
SELF_IDENT = IDENT_PREFIX + 'self'

FN_GLOBALS = {
    (NONE_IDENT := IDENT_PREFIX + 'None'): None,
    (TYPE_ERROR_IDENT := IDENT_PREFIX + 'TypeError'): TypeError,

    (OBJECT_SETATTR_IDENT := IDENT_PREFIX + 'object_setattr'): object.__setattr__,

    (FROZEN_INSTANCE_ERROR_IDENT := IDENT_PREFIX + 'FrozenInstanceError'): dc.FrozenInstanceError,
    (MISSING_IDENT := IDENT_PREFIX + 'MISSING'): dc.MISSING,
}
