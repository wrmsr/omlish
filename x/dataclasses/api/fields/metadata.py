import dataclasses as dc
import typing as ta

from omlish import check
from omlish import lang

from ...specs import FieldSpec
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


def update_field_metadata(
        f: dc.Field,
        metadata: ta.Mapping[ta.Any, ta.Any],
) -> None:
    md: ta.Any = f.metadata

    mdu: dict = {}
    for k, v in metadata.items():
        if md is None or md.get(k) != v:
            mdu[k] = v  # noqa
    if not mdu:
        return

    if md is None:
        ms = [mdu]
    else:
        ms = [mdu, md]

    f.metadata = chain_mapping_proxy(*ms)


def set_field_spec_metadata(
        f: dc.Field,
        fs: FieldSpec,
) -> None:
    update_field_metadata(
        f,
        {
            FieldSpec: fs,
            _ExtraFieldParamsMetadata: {},
        },
    )
