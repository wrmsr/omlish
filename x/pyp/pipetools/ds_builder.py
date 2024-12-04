from functools import partial

from .main import StringFormatter
from .main import XObject


class NoBuilder(ValueError):
    pass


def DSBuilder(definition):
    builder = select_builder(definition)
    if builder:
        return builder(definition)
    raise NoBuilder("Don't know how to build %s" % type(definition))


def SequenceBuilder(cls, definition):
    return lambda x: cls(ds_item(d, x) for d in definition)


def DictBuilder(definition):
    return lambda x: dict(
        (ds_item(key_def, x), ds_item(val_def, x))
        for key_def, val_def in definition.items())


builders = {
    tuple: partial(SequenceBuilder, tuple),
    list: partial(SequenceBuilder, list),
    dict: DictBuilder,
}


def select_builder(definition):
    for cls, builder in builders.items():
        if isinstance(definition, cls):
            return builder


def ds_item(definition, data):
    if isinstance(definition, XObject):
        return (~definition)(data)
    if isinstance(definition, str):
        return StringFormatter(definition)(data)
    if callable(definition):
        return definition(data)
    try:
        return DSBuilder(definition)(data)
    except NoBuilder:
        # static item
        return definition
