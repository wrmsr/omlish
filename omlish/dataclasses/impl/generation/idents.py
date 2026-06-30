IDENT_PREFIX = '__dataclass__'

SELF_IDENT = IDENT_PREFIX + 'self'
SELF_DICT_IDENT = IDENT_PREFIX + 'self_dict'
VALUE_IDENT = IDENT_PREFIX + 'value'

# Class ident is special - the class may be rebuilt after adding generated methods (primarily for slots), and if so the
# `__class__` closure cell for generated methods is updated to the newly rebuilt class. We could probably do something
# different, but we'll opt to remain strictly equivalent.
CLS_IDENT = '__class__'
