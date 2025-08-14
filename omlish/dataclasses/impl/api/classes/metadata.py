import dataclasses as dc
import typing as ta

from ..... import check
from ..... import lang
from .....lite.dataclasses import is_immediate_dataclass
from ....specs import InitFn


T = ta.TypeVar('T')


##


METADATA_ATTR = '__dataclass_metadata__'


def _get_cls_metadata_dct(cls: type) -> dict:
    check.isinstance(cls, type)
    if is_immediate_dataclass(cls):
        raise TypeError(f'Cannot alter dataclass metadata on already processed class {cls!r}')
    try:
        return cls.__dict__[METADATA_ATTR]
    except KeyError:
        pass
    dct: dict = {}
    setattr(cls, METADATA_ATTR, dct)
    return dct


def _append_cls_metadata(cls, k, v):
    _get_cls_metadata_dct(cls).setdefault(k, []).append(v)


def _append_cls_dct_metadata(k, *vs):
    lang.get_caller_cls_dct(1).setdefault(METADATA_ATTR, {}).setdefault(k, []).extend(vs)


##


class _ExtraClassParamsMetadata(lang.Marker):
    pass


def extra_class_params(**kwargs):
    def inner(cls):
        _append_cls_metadata(cls, _ExtraClassParamsMetadata, kwargs)
        return cls
    return inner


##


class _UserMetadata(lang.Marker):
    pass


def metadata(*objs) -> None:
    _append_cls_dct_metadata(_InitMetadata, *objs)


def append_class_metadata(cls: type[T], *args: ta.Any) -> type[T]:
    _append_cls_metadata(cls, _UserMetadata, *args)
    return cls


#


class _InitMetadata(lang.Marker):
    pass


def init(obj):
    _append_cls_dct_metadata(_InitMetadata, obj)
    return obj


#


class _ValidateMetadata(lang.Marker):
    pass


def validate(obj):
    _append_cls_dct_metadata(_ValidateMetadata, obj)
    return obj


##


@dc.dataclass(frozen=True, kw_only=True, eq=False)
class ClassMetadata:
    extra_params: ta.Mapping[str, ta.Any] | None = None

    user_metadata: ta.Sequence[ta.Any] | None = None
    init_fns: ta.Sequence[InitFn | property] | None = None
    validate_fns: ta.Sequence[ta.Any] | None = None


def extract_cls_metadata(
        cls: type,
        *,
        deep: bool,
) -> ClassMetadata:
    extra_params = {}

    user_metadata: list[ta.Any] = []
    init_fns: list[InitFn | property] = []
    validate_fns: list[ta.Any] = []

    for b_cls in (cls.__mro__[-2::-1] if deep else (cls,)):
        cls_md_dct = b_cls.__dict__.get(METADATA_ATTR, {})

        if b_cls is cls:
            for kw in cls_md_dct.get(_ExtraClassParamsMetadata, []):
                extra_params.update(kw)

        user_metadata.extend(cls_md_dct.get(_UserMetadata) or [])
        init_fns.extend(cls_md_dct.get(_InitMetadata) or [])
        validate_fns.extend(cls_md_dct.get(_ValidateMetadata) or [])

    return ClassMetadata(
        extra_params=extra_params or None,

        user_metadata=user_metadata,
        init_fns=init_fns,
        validate_fns=validate_fns,
    )
