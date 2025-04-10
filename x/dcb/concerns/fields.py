import dataclasses as dc
import types
import typing as ta

from omlish import check

from ..inspect import FieldsInspection
from ..inspect import get_cls_annotations
from ..processing import ProcessingContext
from ..processing import Processor
from ..registry import register_context_item_factory
from ..specs import FieldSpec
from ..specs import FieldType
from ..std.internals import STD_FIELDS_ATTR
from ..std.internals import StdFieldType
from ..std.internals import std_is_classvar
from ..std.internals import std_is_initvar
from ..std.internals import std_is_kw_only


##


InstanceFields = ta.NewType('InstanceFields', ta.Sequence[FieldSpec])


def get_instance_fields(fields: ta.Iterable[FieldSpec]) -> InstanceFields:
    return InstanceFields([f for f in fields if f.field_type is FieldType.INSTANCE])


@register_context_item_factory(InstanceFields)
def _instance_fields_context_item_factory(ctx: ProcessingContext) -> InstanceFields:
    return get_instance_fields(ctx.cs.fields)


##


class InitFields(ta.NamedTuple):
    all: ta.Sequence[FieldSpec]
    ordered: ta.Sequence[FieldSpec]
    std: ta.Sequence[FieldSpec]
    kw_only: ta.Sequence[FieldSpec]


def calc_init_fields(
        fields: ta.Iterable[FieldSpec],
        *,
        reorder: bool,
) -> InitFields:
    all_init_fields = [
        f
        for f in fields
        if f.field_type in (FieldType.INSTANCE, FieldType.INIT)
    ]

    ordered_init_fields = list(all_init_fields)
    if reorder:
        ordered_init_fields.sort(key=lambda f: (f.default.present, not f.kw_only))

    std_init_fields, kw_only_init_fields = (
        tuple(f1 for f1 in ordered_init_fields if f1.init and not f1.kw_only),
        tuple(f1 for f1 in ordered_init_fields if f1.init and f1.kw_only),
    )

    return InitFields(
        all=all_init_fields,
        ordered=ordered_init_fields,
        std=std_init_fields,
        kw_only=kw_only_init_fields,
    )


@register_context_item_factory(InitFields)
def _init_fields_context_item_factory(ctx: ProcessingContext) -> InitFields:
    return calc_init_fields(
        ctx.cs.fields,
        reorder=ctx.cs.reorder,
    )


##


def build_std_field(
        cls: type,
        a_name: str,
        a_type: ta.Any,
        *,
        default_kw_only: bool,
) -> dc.Field:
    default: ta.Any = getattr(cls, a_name, dc.MISSING)
    if isinstance(default, dc.Field):
        f = default
    else:
        if isinstance(default, types.MemberDescriptorType):
            # This is a field in __slots__, so it has no default value.
            default = dc.MISSING
        f = dc.field(default=default)

    f.name = a_name
    f.type = a_type

    ft = StdFieldType.INSTANCE
    if std_is_classvar(cls, f.type):
        ft = StdFieldType.CLASS
    if std_is_initvar(cls, f.type):
        ft = StdFieldType.INIT
    if ft in (StdFieldType.CLASS, StdFieldType.INIT):
        if f.default_factory is not dc.MISSING:
            raise TypeError(f'field {f.name} cannot have a default factory')
    f._field_type = ft.value  # type: ignore  # noqa

    if ft in (StdFieldType.INSTANCE, StdFieldType.INIT):
        if f.kw_only is dc.MISSING:
            f.kw_only = default_kw_only
    else:
        check.arg(ft is StdFieldType.CLASS)
        if f.kw_only is not dc.MISSING:
            raise TypeError(f'field {f.name} is a ClassVar but specifies kw_only')

    if ft is StdFieldType.INSTANCE and f.default is not dc.MISSING and f.default.__class__.__hash__ is None:
        raise ValueError(f'mutable default {type(f.default)} for field {f.name} is not allowed: use default_factory')

    return f


#


@dc.dataclass(frozen=True)
class BuiltClsStdFields:
    fields: ta.Mapping[str, dc.Field]

    _: dc.KW_ONLY

    setattrs: ta.Mapping[str, ta.Any] | None = None
    delattrs: ta.AbstractSet[str] | None = None


def build_cls_std_fields(
        cls: type,
        *,
        kw_only: bool,
) -> BuiltClsStdFields:
    fields: dict[str, dc.Field] = {}

    for b in cls.__mro__[-1:0:-1]:
        base_fields = getattr(b, STD_FIELDS_ATTR, None)
        if base_fields is not None:
            for f in base_fields.values():
                fields[f.name] = f

    cls_annotations = get_cls_annotations(cls)

    cls_fields: list[dc.Field] = []

    kw_only_seen = False
    for name, ann in cls_annotations.items():
        if std_is_kw_only(cls, ann):
            if kw_only_seen:
                raise TypeError(f'{name!r} is KW_ONLY, but KW_ONLY has already been specified')
            kw_only_seen = True
            kw_only = True

        else:
            cls_fields.append(build_std_field(
                cls,
                name,
                ann,
                default_kw_only=kw_only,
            ))

    setattrs: dict[str, ta.Any] = {}
    delattrs: set[str] = set()
    for f in cls_fields:
        fields[f.name] = f
        if isinstance(getattr(cls, f.name, None), dc.Field):
            if f.default is dc.MISSING:
                delattrs.add(f.name)
            else:
                setattrs[f.name] = f.default

    for name, value in cls.__dict__.items():
        if isinstance(value, dc.Field) and name not in cls_annotations:
            raise TypeError(f'{name!r} is a field but has no type annotation')

    return BuiltClsStdFields(
        fields,
        setattrs=setattrs,
        delattrs=delattrs,
    )


@register_context_item_factory(BuiltClsStdFields)
def _built_cls_std_fields_context_item_factory(ctx: ProcessingContext) -> BuiltClsStdFields:
    return build_cls_std_fields(
        ctx.cls,
        kw_only=ctx.cs.kw_only,
    )


##


StdFields = ta.NewType('StdFields', ta.Mapping[str, dc.Field])


@register_context_item_factory(StdFields)
def _std_fields_context_item_factory(ctx: ProcessingContext) -> StdFields:
    return StdFields(ctx[BuiltClsStdFields].fields)


##


@register_context_item_factory(FieldsInspection)
def _fields_inspection_context_item_factory(ctx: ProcessingContext) -> FieldsInspection:
    return FieldsInspection(
        ctx.cls,
        cls_fields=ctx[StdFields],
    )


##


class FieldsProcessor(Processor):
    def check(self) -> None:
        check.not_none(self._ctx[BuiltClsStdFields])

    def process(self, cls: type) -> type:
        csf = self._ctx[BuiltClsStdFields]

        for sak, sav in (csf.setattrs or {}).items():
            setattr(cls, sak, sav)

        for dak in csf.delattrs or []:
            delattr(cls, dak)

        setattr(cls, STD_FIELDS_ATTR, csf.fields)

        return cls
