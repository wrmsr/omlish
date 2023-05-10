import typing as ta

from .types import ClassMetadataKwargHandler
from .types import Extras
from .types import FieldMetadataKwargHandler
from .types import Metadata
from .types import METADATA_ATTR


_FIELD_METADATA_KWARG_HANDLERS: ta.Dict[str, FieldMetadataKwargHandler] = {}
_CLASS_METADATA_KWARG_HANDLERS: ta.Dict[str, ClassMetadataKwargHandler] = {}


def _register_metadata_kwarg_handler(dct, name, fn=None):
    def inner(ifn):
        if not name or name in dct:
            raise KeyError(name)
        if not callable(ifn):
            raise TypeError(ifn)
        dct[name] = ifn
        return ifn
    if fn is not None:
        return inner(fn)
    else:
        return inner


def register_field_metadata_kwarg_handler(
        name: str,
        fn: ta.Optional[FieldMetadataKwargHandler] = None,
) -> ta.Union[FieldMetadataKwargHandler, ta.Callable[[FieldMetadataKwargHandler], FieldMetadataKwargHandler]]:
    return _register_metadata_kwarg_handler(_FIELD_METADATA_KWARG_HANDLERS, name, fn)


def register_class_metadata_kwarg_handler(
        name: str,
        fn: ta.Optional[ClassMetadataKwargHandler] = None,
) -> ta.Union[ClassMetadataKwargHandler, ta.Callable[[ClassMetadataKwargHandler], ClassMetadataKwargHandler]]:
    return _register_metadata_kwarg_handler(_CLASS_METADATA_KWARG_HANDLERS, name, fn)


def _update_kwargs_metadata(dct, obj, kwargs, metadata):
    for k, v in kwargs.items():
        if k in metadata:
            raise
        h = dct[k]
        m = h(obj, v)
        if m is None:
            continue
        if type(m) in metadata:
            raise KeyError(type(m))
        metadata[type(m)] = m
    return metadata


def update_field_kwargs_metadata(fld, kwargs, metadata):
    return _update_kwargs_metadata(_FIELD_METADATA_KWARG_HANDLERS, fld, kwargs, metadata)


def update_class_kwargs_metadata(cls, kwargs):
    kw_md = _update_kwargs_metadata(_CLASS_METADATA_KWARG_HANDLERS, cls, kwargs, {})
    if METADATA_ATTR in cls.__dict__:
        cls_md = getattr(cls, METADATA_ATTR)
    else:
        cls_md = {}
        setattr(cls, METADATA_ATTR, cls_md)
    md = Metadata(kw_md)
    cls_md.setdefault(Extras, []).append(md)
    return md


def get_registered_class_metadata_kwargs() -> ta.AbstractSet[str]:
    return frozenset(_CLASS_METADATA_KWARG_HANDLERS)
