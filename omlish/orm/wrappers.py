from .backrefs import _BACKREF_TYPES
from .keys import _KEY_TYPES
from .refs import _REF_TYPES
from .values import _VALUE_TYPES


#

WRAPPER_TYPES: tuple[type, ...] = (
    *_BACKREF_TYPES,
    *_KEY_TYPES,
    *_REF_TYPES,
    *_VALUE_TYPES,
)
