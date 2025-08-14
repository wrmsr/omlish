import dataclasses as dc
import typing as ta

from ..... import check
from ..... import lang
from ....debug import DEBUG
from ....specs import FieldSpec
from ....tools.modifiers import field_modifier
from ...utils import chain_mapping_proxy


##


class _ExtraFieldParamsMetadata(lang.Marker):
    pass


def extra_field_params(**kwargs: ta.Any) -> ta.Mapping[ta.Any, ta.Any]:
    return {_ExtraFieldParamsMetadata: kwargs}


##


def get_field_spec(f: dc.Field) -> FieldSpec | None:
    try:
        fs = f.metadata[FieldSpec]
    except KeyError:
        return None

    return check.isinstance(fs, FieldSpec)


##


def set_field_metadata(
        f: dc.Field,
        metadata: ta.Mapping[ta.Any, ta.Any],
) -> dc.Field:
    if DEBUG:
        check.isinstance(f, dc.Field)

    md: ta.Any = f.metadata

    mdu: dict = {}
    for k, v in metadata.items():
        if md is None or md.get(k) != v:
            mdu[k] = v  # noqa
    if not mdu:
        return f

    if md is None:
        ms = [mdu]
    else:
        ms = [mdu, md]

    f.metadata = chain_mapping_proxy(*ms)
    return f


#


def set_field_spec_metadata(
        f: dc.Field,
        fs: FieldSpec,
) -> None:
    set_field_metadata(
        f,
        {
            FieldSpec: fs,
            _ExtraFieldParamsMetadata: {},
        },
    )


##


def update_extra_field_params(
        f: dc.Field,
        *,
        unless_non_default: bool = False,
        **kwargs: ta.Any,
) -> dc.Field:
    fe = f.metadata.get(_ExtraFieldParamsMetadata, {})
    return set_field_metadata(f, {
        _ExtraFieldParamsMetadata: {
            **(fe if not unless_non_default else {}),
            **kwargs,
            **(fe if unless_non_default else {}),
        },
    })


def with_extra_field_params(**kwargs: ta.Any) -> field_modifier:
    @field_modifier
    def inner(f: dc.Field) -> dc.Field:
        return update_extra_field_params(f, **kwargs)
    return inner
