import dataclasses as dc
import typing as ta

from .. import lang


METADATA_KEY = '__dataclass_metadata__'

MERGED_KEYS: ta.Set[ta.Any] = set()


def _merged(o):
    MERGED_KEYS.add(o)
    return o


def metadata(class_or_instance: ta.Any) -> ta.Mapping[ta.Any, ta.Any]:
    cls = class_or_instance if isinstance(class_or_instance, type) else type(class_or_instance)
    if not dc.is_dataclass(cls):
        raise TypeError('must be called with a dataclass type or instance')
    dct: ta.Dict[ta.Any, ta.Any] = {}
    for scls in reversed(cls.__mro__):
        smd = scls.__dict__.get(METADATA_KEY)
        if not smd:
            continue
        for k, v in smd.items():
            if k in MERGED_KEYS:
                dct.setdefault(k, []).extend(v)
            else:
                dct[k] = v
    return dct


def _add_cls_md(k, v):
    lang.get_caller_cls_dct(1).setdefault(METADATA_KEY, {}).setdefault(k, []).append(v)


##


@_merged
class Check(lang.Marker):
    pass


def check(fn: ta.Union[ta.Callable[..., bool], staticmethod]) -> None:
    _add_cls_md(Check, fn)


##


@_merged
class Init(lang.Marker):
    pass


def init(fn: ta.Callable[..., None]) -> None:
    _add_cls_md(Init, fn)
