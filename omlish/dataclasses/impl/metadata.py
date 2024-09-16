import types
import typing as ta

from ... import lang


METADATA_ATTR = '__dataclass_metadata__'

Metadata: ta.TypeAlias = ta.Mapping[ta.Any, ta.Any]

EMPTY_METADATA: Metadata = types.MappingProxyType({})

_CLASS_MERGED_KEYS: set[str] = set()
CLASS_MERGED_KEYS: ta.AbstractSet = _CLASS_MERGED_KEYS


def _class_merged(o):
    _CLASS_MERGED_KEYS.add(o)
    return o


def get_merged_metadata(obj: ta.Any) -> Metadata:
    cls = obj if isinstance(obj, type) else type(obj)
    dct: dict[ta.Any, ta.Any] = {}
    for cur in cls.__mro__[::-1]:
        if not (smd := cur.__dict__.get(METADATA_ATTR)):
            continue
        for k, v in smd.items():
            if k in CLASS_MERGED_KEYS:
                dct.setdefault(k, []).extend(v)
            else:
                dct[k] = v
    return dct


def _append_cls_md(k, v):
    lang.get_caller_cls_dct(1).setdefault(METADATA_ATTR, {}).setdefault(k, []).append(v)


##


@_class_merged
class UserMetadata(lang.Marker):
    pass


@lang.cls_dct_fn()
def metadata(cls_dct, *args) -> None:
    cls_dct.setdefault(METADATA_ATTR, {}).setdefault(UserMetadata, []).extend(args)


##


@_class_merged
class Validate(lang.Marker):
    pass


def validate(fn: ta.Callable[..., bool] | staticmethod) -> None:
    _append_cls_md(Validate, fn)


##


@_class_merged
class Init(lang.Marker):
    pass


def init(obj):
    _append_cls_md(Init, obj)
    return obj
