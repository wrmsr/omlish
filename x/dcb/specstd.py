import dataclasses as dc
import typing as ta

from omlish import check
from omlish import lang

from .specs import ClassSpec
from .specs import DefaultFactory
from .specs import FieldSpec
from .specs import FieldType
from .std import StdFieldType
from .std import StdParams
from .std import std_field_type


##


# def field(
#     *,
#     default=MISSING,
#     default_factory=MISSING,
#     init=True,
#     repr=True,
#     hash=None,
#     compare=True,
#     metadata=None,
#     kw_only=MISSING,
#     # doc=None,  # 3.14
# ):


#


STD_FIELD_TYPE_BY_SPEC_FIELD_TYPE: ta.Mapping[FieldType, StdFieldType] = {
    FieldType.INSTANCE: StdFieldType.INSTANCE,
    FieldType.CLASS: StdFieldType.CLASS,
    FieldType.INIT: StdFieldType.INIT,
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

    elif default_factory is not None:
        return lang.just(DefaultFactory(default_factory))

    else:
        return lang.empty()


def std_field_to_spec_field_default(f: dc.Field) -> lang.Maybe[ta.Any]:
    return std_to_spec_field_default(
        default=f.default,
        default_factory=f.default_factory,
    )


#


def field_spec_to_std_field(fs: FieldSpec) -> dc.Field:
    f = dc.Field(
        default=...,
        default_factory=...,
        init=check.isinstance(fs.init, bool),
        repr=check.isinstance(fs.repr, bool),
        hash=...,
        compare=check.isinstance(fs.compare, bool),
        metadata=fs.metadata,
        kw_only=...,
    )
    f.name = fs.name
    f.type = fs.annotation
    f._field_type = STD_FIELD_TYPE_BY_SPEC_FIELD_TYPE[fs.field_type]  # noqa
    return f


def std_field_to_field_spec(f: dc.Field) -> FieldSpec:
    return FieldSpec(
        name=check.non_empty_str(f.name),
        annotation=check.is_not(f.type, dc.MISSING),

        default=std_field_to_spec_field_default(f),

        init=check.isinstance(f.init, bool),
        repr=check.isinstance(f.repr, bool),
        hash=...,
        compare=check.isinstance(f.compare, bool),
        metadata=...,
        kw_only=...,

        field_type=SPEC_FIELD_TYPE_BY_STD_FIELD_TYPE[std_field_type(f)],
    )


##


# def dataclass(
#     cls=None,
#     /,
#     *,
#
#     init=True,
#     repr=True,
#     eq=True,
#     order=False,
#     unsafe_hash=False,
#     frozen=False,
#
#     match_args=True,
#     kw_only=False,
#     slots=False,
#     weakref_slot=False,
# ):


#


def class_spec_to_std_params(cs: ClassSpec) -> StdParams:
    return StdParams(
        init=cs.init,
        repr=cs.repr,
        eq=cs.eq,
        order=cs.order,
        unsafe_hash=cs.unsafe_hash,
        frozen=cs.frozen,

        match_args=cs.match_args,
        kw_only=cs.kw_only,
        slots=cs.slots,
        weakref_slot=cs.weakref_slot,
    )


def std_params_to_class_spec(
        p: StdParams,
        fields: ta.Sequence[FieldSpec],
) -> ClassSpec:
    return ClassSpec(
        fields=fields,

        init=check.isinstance(p.init, bool),
        repr=check.isinstance(p.repr, bool),
        eq=check.isinstance(p.eq, bool),
        order=check.isinstance(p.order, bool),
        unsafe_hash=check.isinstance(p.unsafe_hash, bool),
        frozen=check.isinstance(p.frozen, bool),

        match_args=check.isinstance(p.match_args, bool),
        kw_only=check.isinstance(p.kw_only, bool),
        slots=check.isinstance(p.slots, bool),
        weakref_slot=check.isinstance(p.weakref_slot, bool),
    )
