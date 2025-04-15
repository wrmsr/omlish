import dataclasses as dc
import typing as ta

from omlish import check
from omlish import lang

from ...internals import StdFieldType
from ...internals import std_field_type
from ...specs import DefaultFactory
from ...specs import FieldSpec
from ...specs import FieldType
from .metadata import _ExtraParams


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
    efp = f.metadata.get(_ExtraParams, {})

    return FieldSpec(
        name=check.non_empty_str(f.name),
        annotation=check.is_not(f.type, dc.MISSING),

        default=std_field_to_spec_field_default(f),

        init=check.isinstance(f.init, bool),
        repr=check.isinstance(f.repr, bool),
        hash=check.isinstance(f.hash, (bool, None)),
        compare=check.isinstance(f.compare, bool),
        metadata=f.metadata,
        kw_only=None if f.kw_only is dc.MISSING else check.isinstance(f.kw_only, bool),

        field_type=SPEC_FIELD_TYPE_BY_STD_FIELD_TYPE[std_field_type(f)],

        **lang.opt_kw(
            coerce=efp.get('coerce'),
            validate=efp.get('validate'),
            check_type=efp.get('check_type'),
            override=efp.get('override'),
            repr_fn=efp.get('repr_fn'),
            repr_priority=efp.get('repr_priority'),
        ),
    )
