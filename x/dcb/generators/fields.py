import typing as ta

from ..specs import FieldSpec
from ..specs import FieldType


##


class InitFields(ta.NamedTuple):
    all: ta.Sequence[FieldSpec]
    ordered: ta.Sequence[FieldSpec]
    std: ta.Sequence[FieldSpec]
    kw_only: ta.Sequence[FieldSpec]


def get_init_fields(
        fields: ta.Iterable[FieldSpec],
        *,
        reorder: bool = False,
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
