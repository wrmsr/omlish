"""
TODO:
 - __deepcopy__
"""
import dataclasses as dc

from .fields import field_type
from .internals import FIELDS_ATTR
from .internals import FieldType
from .processing import Processor
from .utils import set_new_attribute


MISSING = dc.MISSING


def _copy(obj):
    kw = {}

    for f in getattr(obj, FIELDS_ATTR).values():
        if field_type(f) is FieldType.CLASS:
            continue
        kw[f.name] = getattr(obj, f.name)

    return obj.__class__(**kw)


class CopyProcessor(Processor):
    def _process(self) -> None:
        set_new_attribute(self._cls, '__copy__', _copy)
