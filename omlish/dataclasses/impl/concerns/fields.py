import dataclasses as dc
import typing as ta

from .... import check
from ..._internals import STD_FIELDS_ATTR
from ...debug import DEBUG
from ...inspect import FieldsInspection
from ...specs import FieldSpec
from ...specs import FieldType
from ..generation.idents import IDENT_PREFIX
from ..processing.base import ProcessingContext
from ..processing.base import Processor
from ..processing.priority import ProcessorPriority
from ..processing.registry import register_processing_context_item_factory
from ..processing.registry import register_processor_type


##


class InstanceFields(list[FieldSpec]):
    pass


def get_instance_fields(fields: ta.Iterable[FieldSpec]) -> InstanceFields:
    return InstanceFields([f for f in fields if f.field_type is FieldType.INSTANCE])


@register_processing_context_item_factory(InstanceFields)
def _instance_fields_processing_context_item_factory(ctx: ProcessingContext) -> InstanceFields:
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
        class_kw_only: bool,
) -> InitFields:
    all_init_fields = [
        f
        for f in fields
        if f.field_type in (FieldType.INSTANCE, FieldType.INIT_VAR)
    ]

    def f_kw_only(f: FieldSpec) -> bool:
        return f.kw_only if f.kw_only is not None else class_kw_only

    ordered_init_fields = list(all_init_fields)
    if reorder:
        ordered_init_fields.sort(key=lambda f: (f.default.present, not f_kw_only(f)))

    std_init_fields = tuple(f1 for f1 in ordered_init_fields if f1.init and not f_kw_only(f1))
    kw_only_init_fields = tuple(f1 for f1 in ordered_init_fields if f1.init and f_kw_only(f1))

    return InitFields(
        all=all_init_fields,
        ordered=ordered_init_fields,
        std=std_init_fields,
        kw_only=kw_only_init_fields,
    )


@register_processing_context_item_factory(InitFields)
def _init_fields_processing_context_item_factory(ctx: ProcessingContext) -> InitFields:
    return calc_init_fields(
        ctx.cs.fields,
        reorder=ctx.cs.reorder,
        class_kw_only=ctx.cs.kw_only,
    )


##


StdFields = ta.NewType('StdFields', ta.Mapping[str, dc.Field])


@register_processing_context_item_factory(StdFields)
def _std_fields_processing_context_item_factory(ctx: ProcessingContext) -> StdFields:
    fld_dct = ctx.cls.__dict__[STD_FIELDS_ATTR]
    for fn, f in fld_dct.items():
        if DEBUG:
            check.isinstance(f, dc.Field)
        check.equal(f.name, fn)
    check.equal(set(fld_dct), set(ctx.cs.fields_by_name))
    return StdFields(fld_dct)


##


@register_processing_context_item_factory(FieldsInspection)
def _fields_inspection_processing_context_item_factory(ctx: ProcessingContext) -> FieldsInspection:
    return FieldsInspection(
        ctx.cls,
        cls_fields=ctx[StdFields],
    )


##


@register_processor_type(priority=ProcessorPriority.BOOTSTRAP)
class FieldsProcessor(Processor):
    def check(self) -> None:
        check.not_none(self._ctx[StdFields])
        for f in self._ctx.cs.fields:
            check.arg(not f.name.startswith(IDENT_PREFIX))
