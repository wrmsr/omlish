import dataclasses as dc
import typing as ta

from omlish import lang

from ..specs import InitFn


##


METADATA_ATTR = '__dataclass_metadata__'


def _append_cls_md(k, v):
    lang.get_caller_cls_dct(1).setdefault(METADATA_ATTR, {}).setdefault(k, []).append(v)


##


class _InitMetadata(lang.Marker):
    pass


def init(obj):
    _append_cls_md(_InitMetadata, obj)
    return obj


#


class _ValidateMetadata(lang.Marker):
    pass


def validate(obj):
    _append_cls_md(_ValidateMetadata, obj)
    return obj


##


@dc.dataclass(frozen=True, kw_only=True, eq=False)
class ClassMetadata:
    init_fns: ta.Sequence[InitFn] | None = None
    validate_fns: ta.Sequence[ta.Any] | None = None


def extract_cls_metadata(cls: type) -> ClassMetadata:
    cls_md_dct = cls.__dict__.get(METADATA_ATTR, {})
    return ClassMetadata(
        init_fns=cls_md_dct.get(_InitMetadata),
        validate_fns=cls_md_dct.get(_ValidateMetadata),
    )


def remove_cls_metadata(cls: type) -> None:
    try:
        delattr(cls, METADATA_ATTR)
    except AttributeError:
        pass
