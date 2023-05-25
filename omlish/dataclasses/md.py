"""
TODO:
 - class and/or field usage enforcement / codification
"""
import dataclasses as dc
import typing as ta

from .. import collections as col
from .. import lang


Metadata = ta.Mapping[ta.Any, ta.Any]

METADATA_KEY = '__dataclass_metadata__'

CLASS_MERGED_KEYS: ta.Set[ta.Any] = set()


def _class_merged(o):
    CLASS_MERGED_KEYS.add(o)
    return o


def metadata(class_or_instance: ta.Any) -> Metadata:
    cls = class_or_instance if isinstance(class_or_instance, type) else type(class_or_instance)
    if not dc.is_dataclass(cls):
        raise TypeError('must be called with a dataclass type or instance')
    dct: ta.Dict[ta.Any, ta.Any] = {}
    for scls in reversed(cls.__mro__):
        smd = scls.__dict__.get(METADATA_KEY)
        if not smd:
            continue
        for k, v in smd.items():
            if k in CLASS_MERGED_KEYS:
                dct.setdefault(k, []).extend(v)
            else:
                dct[k] = v
    return dct


def tag(*args, **kwargs):
    cls = None
    if len(args) > 0:
        if isinstance(args[0], type):
            cls, args = args[0], args[1:]

    def inner(cls):
        if not (isinstance(cls, type) and dc.is_dataclass(cls)):
            raise TypeError('must be called with a dataclass type')
        try:
            cmd = cls.__dict__[METADATA_KEY]
        except KeyError:
            cmd = {}
            setattr(cls, METADATA_KEY, cmd)
        for k, v in col.yield_dict_init(*args, **kwargs):
            cmd[k] = v
        return cls

    if cls is None:
        return inner
    else:
        inner(cls)


def _add_cls_md(k, v):
    lang.get_caller_cls_dct(1).setdefault(METADATA_KEY, {}).setdefault(k, []).append(v)


##


@_class_merged
class Check(lang.Marker):
    pass


def check(fn: ta.Union[ta.Callable[..., bool], staticmethod]) -> None:
    _add_cls_md(Check, fn)


##


@_class_merged
class Init(lang.Marker):
    pass


def init(fn: ta.Callable[..., None]) -> None:
    _add_cls_md(Init, fn)


##


class KwOnly(lang.Marker):
    pass


##


class Coerce(lang.Marker):
    pass
