import dataclasses as dc

from ..processing.base import Processor
from ..processing.registry import register_processor_type
from ..processing.priority import ProcessorPriority
from ..std.internals import STD_FIELDS_ATTR
from ..std.internals import StdFieldType
from ..std.internals import std_field_type
from ..std.internals import std_is_dataclass_instance
from ..utils import set_new_attribute


##


def replace(obj, /, **changes):  # noqa
    if not std_is_dataclass_instance(obj):
        raise TypeError('replace() should be called on dataclass instances')
    return _replace(obj, **changes)


def _replace(obj, /, **changes):
    for f in getattr(obj, STD_FIELDS_ATTR).values():
        if (ft := std_field_type(f)) is StdFieldType.CLASS:
            continue

        if not f.init:
            if f.name in changes:
                raise TypeError(f'field {f.name} is declared with init=False, it cannot be specified with replace()')
            continue

        if f.name not in changes:
            if ft is StdFieldType.INIT and f.default is dc.MISSING:
                raise TypeError(f'InitVar {f.name!r} must be specified with replace()')
            changes[f.name] = getattr(obj, f.name)

    return obj.__class__(**changes)


@register_processor_type(priority=ProcessorPriority.POST_GENERATION)
class ReplaceProcessor(Processor):
    def process(self, cls: type) -> type:
        set_new_attribute(cls, '__replace__', _replace)
        return cls
