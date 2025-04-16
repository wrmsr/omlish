import dataclasses as dc
import typing as ta

from omlish import check
from omlish import lang

from ...debug import DEBUG
from ...internals import StdFieldType
from ...internals import std_field_type
from ...specs import DefaultFactory
from ...specs import FieldSpec
from ...specs import FieldType
from .metadata import _ExtraFieldParamsMetadata
from .metadata import set_field_spec_metadata


##


STD_FIELD_TYPE_BY_SPEC_FIELD_TYPE: ta.Mapping[FieldType, StdFieldType] = {
    FieldType.INSTANCE: StdFieldType.INSTANCE,
    FieldType.CLASS_VAR: StdFieldType.CLASS_VAR,
    FieldType.INIT_VAR: StdFieldType.INIT_VAR,
}

SPEC_FIELD_TYPE_BY_STD_FIELD_TYPE = {v: k for k, v in STD_FIELD_TYPE_BY_SPEC_FIELD_TYPE.items()}


#


def std_to_spec_field_default(
        *,
        default: ta.Any,
        default_factory: ta.Any,
) -> lang.Maybe[ta.Any]:
    if default is not dc.MISSING:
        check.state(default_factory is dc.MISSING)
        return lang.just(default)
    elif default_factory is not dc.MISSING:
        return lang.just(DefaultFactory(default_factory))
    else:
        return lang.empty()


def std_field_to_spec_field_default(f: dc.Field) -> lang.Maybe[ta.Any]:
    return std_to_spec_field_default(
        default=f.default,
        default_factory=f.default_factory,
    )


class StdDefaults(ta.NamedTuple):
    default: ta.Any
    default_factory: ta.Any


def spec_field_default_to_std_defaults(dfl: lang.Maybe[DefaultFactory | ta.Any]) -> StdDefaults:
    if not dfl.present:
        return StdDefaults(dc.MISSING, dc.MISSING)
    elif isinstance(dfv := dfl.must(), DefaultFactory):
        return StdDefaults(dc.MISSING, dfv.fn)
    else:
        return StdDefaults(dfv, dc.MISSING)


#


def std_field_to_field_spec(f: dc.Field) -> FieldSpec:
    efp = f.metadata.get(_ExtraFieldParamsMetadata, {})

    return FieldSpec(
        name=check.non_empty_str(f.name),
        annotation=check.is_not(f.type, dc.MISSING),

        default=std_field_to_spec_field_default(f),

        init=check.isinstance(f.init, bool) if DEBUG else f.init,
        repr=check.isinstance(f.repr, bool) if DEBUG else f.repr,
        hash=check.isinstance(f.hash, (bool, None)) if DEBUG else f.hash,
        compare=check.isinstance(f.compare, bool) if DEBUG else f.compare,
        metadata=f.metadata,
        kw_only=None if f.kw_only is dc.MISSING else (check.isinstance(f.kw_only, bool) if DEBUG else f.kw_only),

        **lang.opt_kw(
            coerce=efp.get('coerce'),
            validate=efp.get('validate'),
            check_type=efp.get('check_type'),
            override=efp.get('override'),
            repr_fn=efp.get('repr_fn'),
            repr_priority=efp.get('repr_priority'),
        ),

        field_type=SPEC_FIELD_TYPE_BY_STD_FIELD_TYPE[std_field_type(f)],
    )


##


def field_spec_to_std_field(fs: FieldSpec) -> dc.Field:
    sdf = spec_field_default_to_std_defaults(fs.default)

    f = dc.Field(
        default=sdf.default,
        default_factory=sdf.default_factory,

        init=fs.init,
        repr=fs.repr,
        hash=fs.hash,
        compare=fs.compare,
        **lang.opt_kw(metadata=fs.metadata),
        kw_only=dc.MISSING if fs.kw_only is None else fs.kw_only,  # type: ignore[arg-type]
    )

    f.name = fs.name
    f.type = fs.annotation

    f._field_type = STD_FIELD_TYPE_BY_SPEC_FIELD_TYPE[fs.field_type].value  # type: ignore[attr-defined]  # noqa

    set_field_spec_metadata(f, fs)

    return f


##


def check_field_spec_against_field(f: dc.Field, fs: FieldSpec) -> None:
    f_tup = (
        f.name,
        f.type,

        f.default,
        f.default_factory,

        f.repr,
        f.hash,
        f.init,
        f.compare,
        # f.metadata,
        f.kw_only,

        f._field_type,  # type: ignore[attr-defined]  # noqa
    )

    fs_tup = (
        fs.name,
        fs.annotation,

        *spec_field_default_to_std_defaults(fs.default),

        fs.repr,
        fs.hash,
        fs.init,
        fs.compare,
        # fs.metadata,
        fs.kw_only,

        STD_FIELD_TYPE_BY_SPEC_FIELD_TYPE[fs.field_type].value,
    )

    if f_tup != fs_tup:
        raise RuntimeError(f'Field/FieldSpec mismatch: {f_tup!r} != {fs_tup!r}')
