import dataclasses as dc
import types
import typing as ta

from ..... import check
from ...._internals import STD_FIELDS_ATTR
from ...._internals import StdFieldType
from ...._internals import std_is_classvar
from ...._internals import std_is_initvar
from ...._internals import std_is_kw_only
from ....inspect import get_cls_annotations


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

    # field type

    ft = StdFieldType.INSTANCE
    if std_is_classvar(cls, f.type):
        ft = StdFieldType.CLASS_VAR
    if std_is_initvar(cls, f.type):
        ft = StdFieldType.INIT_VAR
    if ft in (StdFieldType.CLASS_VAR, StdFieldType.INIT_VAR):
        if f.default_factory is not dc.MISSING:
            raise TypeError(f'field {a_name} cannot have a default factory')
    f._field_type = ft.value  # type: ignore[attr-defined]  # noqa

    # kw_only

    if ft in (StdFieldType.INSTANCE, StdFieldType.INIT_VAR):
        if f.kw_only is dc.MISSING:
            f.kw_only = default_kw_only
    else:
        check.arg(ft is StdFieldType.CLASS_VAR)
        if f.kw_only is not dc.MISSING:
            raise TypeError(f'field {a_name} is a ClassVar but specifies kw_only')

    # defaults

    if (
            ft is StdFieldType.INSTANCE and
            f.default is not dc.MISSING and
            f.default.__class__.__hash__ is None
    ):
        raise ValueError(f'mutable default {type(f.default)} for field {a_name} is not allowed: use default_factory')

    #

    return f


##


def build_cls_std_fields(
        cls: type,
        *,
        kw_only: bool,
) -> ta.Mapping[str, dc.Field]:
    fields: dict[str, dc.Field] = {}

    for b in cls.__mro__[-1:0:-1]:
        if not (base_fields := getattr(b, STD_FIELDS_ATTR, None)):
            continue
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

    for f in cls_fields:
        fields[f.name] = f
        if isinstance(getattr(cls, f.name, None), dc.Field):
            if f.default is dc.MISSING:
                delattr(cls, f.name)
            else:
                setattr(cls, f.name, f.default)

    for name, value in cls.__dict__.items():
        if isinstance(value, dc.Field) and name not in cls_annotations:
            raise TypeError(f'{name!r} is a field but has no type annotation')

    return fields
