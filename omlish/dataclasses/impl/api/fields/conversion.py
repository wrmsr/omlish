import dataclasses as dc
import sys
import typing as ta

from ..... import check
from ..... import lang
from ...._internals import StdFieldType
from ...._internals import std_field_type
from ....debug import DEBUG
from ....specs import DefaultFactory
from ....specs import FieldSpec
from ....specs import FieldType
from .metadata import _ExtraFieldParamsMetadata
from .metadata import set_field_spec_metadata


##


_IS_PY_3_14 = sys.version_info >= (3, 14)


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


def std_field_to_field_spec(
        f: dc.Field,
        *,
        ignore_metadata: bool = False,
        ignore_extra_params: bool = False,
        set_metadata: bool = False,
) -> FieldSpec:
    if not ignore_metadata:
        try:
            fs = f.metadata[FieldSpec]
        except KeyError:
            pass
        else:
            check_field_spec_against_field(f, fs)
            return fs

    extra_params = {}
    if not ignore_extra_params:
        extra_params.update(f.metadata.get(_ExtraFieldParamsMetadata, {}))

    fs = FieldSpec(
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
            doc=extra_params.get('doc', f.doc if _IS_PY_3_14 else None),  # type: ignore[attr-defined]  # noqa
        ),

        **lang.opt_kw(
            coerce=extra_params.get('coerce'),
            validate=extra_params.get('validate'),
            check_type=extra_params.get('check_type'),
            override=extra_params.get('override'),
            repr_fn=extra_params.get('repr_fn'),
            repr_priority=extra_params.get('repr_priority'),
        ),

        field_type=SPEC_FIELD_TYPE_BY_STD_FIELD_TYPE[std_field_type(f)],
    )

    if set_metadata:
        set_field_spec_metadata(f, fs)

    return fs


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
        **(dict(doc=fs.doc) if _IS_PY_3_14 else {}),
    )

    f.name = fs.name
    f.type = fs.annotation

    f._field_type = STD_FIELD_TYPE_BY_SPEC_FIELD_TYPE[fs.field_type].value  # type: ignore[attr-defined]  # noqa

    set_field_spec_metadata(f, fs)

    return f


##


def check_field_spec_against_field(f: dc.Field, fs: FieldSpec) -> None:
    f_dct = {
        'name': f.name,
        'type': f.type,

        'default': f.default,
        'default_factory': f.default_factory,

        'repr': f.repr,
        'hash': f.hash,
        'init': f.init,
        'compare': f.compare,
        # f.metadata,
        'kw_only': f.kw_only if f.kw_only is not dc.MISSING else None,
        **({'doc': f.doc} if _IS_PY_3_14 else {}),  # type: ignore[attr-defined]  # noqa

        'std_field_type': f._field_type,  # type: ignore[attr-defined]  # noqa
    }

    fs_dct = {
        'name': fs.name,
        'type': fs.annotation,

        **spec_field_default_to_std_defaults(fs.default)._asdict(),

        'repr': fs.repr,
        'hash': fs.hash,
        'init': fs.init,
        'compare': fs.compare,
        # fs.metadata,
        'kw_only': fs.kw_only,
        **({'doc': fs.doc} if _IS_PY_3_14 else {}),

        'std_field_type': STD_FIELD_TYPE_BY_SPEC_FIELD_TYPE[fs.field_type].value,
    }

    if f_dct != fs_dct:
        diff_dct = {
            k: (f_v, fs_v)
            for k, f_v in f_dct.items()
            if (fs_v := fs_dct[k]) != f_v
        }
        raise RuntimeError(f'Field/FieldSpec mismatch: {diff_dct!r}')
