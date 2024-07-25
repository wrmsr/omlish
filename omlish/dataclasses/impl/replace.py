import dataclasses as dc

from .fields import field_type
from .internals import FIELDS_ATTR
from .internals import FieldType
from .internals import is_dataclass_instance
from .processing import Processor
from .utils import set_new_attribute


MISSING = dc.MISSING


def replace(obj, /, **changes):  # noqa
    if not is_dataclass_instance(obj):
        raise TypeError('replace() should be called on dataclass instances')
    return _replace(obj, **changes)


def _replace(obj, /, **changes):
    for f in getattr(obj, FIELDS_ATTR).values():
        if (ft := field_type(f)) is FieldType.CLASS:
            continue

        if not f.init:
            if f.name in changes:
                raise TypeError(f'field {f.name} is declared with init=False, it cannot be specified with replace()')
            continue

        if f.name not in changes:
            if ft is FieldType.INIT and f.default is MISSING:
                raise TypeError(f'InitVar {f.name!r} must be specified with replace()')
            changes[f.name] = getattr(obj, f.name)

    return obj.__class__(**changes)


class ReplaceProcessor(Processor):
    def _process(self) -> None:
        set_new_attribute(self._cls, '__replace__', _replace)
