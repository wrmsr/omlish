import dataclasses as dc
import typing as ta

from omlish import check
from omlish import lang

from ...specs import InitFn


T = ta.TypeVar('T')


##


METADATA_ATTR = '__dataclass_metadata__'


def _append_cls_md(cls, k, v):
    check.isinstance(cls, type)
    check.arg(not dc.is_dataclass(cls))
    try:
        dct = cls.__dict__[METADATA_ATTR]
    except KeyError:
        setattr(cls, METADATA_ATTR, dct := {})
    dct.setdefault(k, []).append(v)


def _append_cls_dct_md(k, *vs):
    lang.get_caller_cls_dct(1).setdefault(METADATA_ATTR, {}).setdefault(k, []).extend(vs)


##


class _ExtraClassParamsMetadata(lang.Marker):
    pass


def extra_class_params(**kwargs):
    def inner(cls):
        _append_cls_md(cls, _ExtraClassParamsMetadata, kwargs)
        return cls
    return inner


##


class _UserMetadata(lang.Marker):
    pass


def metadata(*objs) -> None:
    _append_cls_dct_md(_InitMetadata, *objs)


def update_class_metadata(cls: type[T], *args: ta.Any) -> type[T]:
    check.isinstance(cls, type)
    setattr(cls, METADATA_ATTR, md := getattr(cls, METADATA_ATTR, {}))
    md.setdefault(_UserMetadata, []).extend(args)
    return cls


#


class _InitMetadata(lang.Marker):
    pass


def init(obj):
    _append_cls_dct_md(_InitMetadata, obj)
    return obj


#


class _ValidateMetadata(lang.Marker):
    pass


def validate(obj):
    _append_cls_dct_md(_ValidateMetadata, obj)
    return obj


##


@dc.dataclass(frozen=True, kw_only=True, eq=False)
class ClassMetadata:
    extra_params: ta.Mapping[str, ta.Any] | None = None

    user_metadata: ta.Sequence[ta.Any] | None = None
    init_fns: ta.Sequence[InitFn | property] | None = None
    validate_fns: ta.Sequence[ta.Any] | None = None


def extract_cls_metadata(cls: type) -> ClassMetadata:
    cls_md_dct = cls.__dict__.get(METADATA_ATTR, {})

    eps = {}
    for kw in cls_md_dct.get(_ExtraClassParamsMetadata, []):
        eps.update(kw)

    return ClassMetadata(
        extra_params=eps or None,

        user_metadata=cls_md_dct.get(_UserMetadata),
        init_fns=cls_md_dct.get(_InitMetadata),
        validate_fns=cls_md_dct.get(_ValidateMetadata),
    )
