import collections
import dataclasses as dc
import types
import typing as ta

from omlish import check
from omlish import lang

from ..inspect import get_cls_annotations
from ..std.internals import STD_FIELDS_ATTR
from ..std.internals import StdFieldType
from ..std.internals import std_is_classvar
from ..std.internals import std_is_initvar
from ..std.internals import std_is_kw_only
from ..utils import AttrMods


##


class _ExtraParams(lang.Marker):
    pass


def extra_field_params(**kwargs) -> ta.Mapping[ta.Any, ta.Any]:
    return {_ExtraParams: kwargs}


##


@dc.dataclass(frozen=True)
class BuiltStdField:
    fld: dc.Field
    name: str
    type: str

    _: dc.KW_ONLY

    attr_mods: AttrMods | None = None


def build_std_field(
        cls: type,
        a_name: str,
        a_type: ta.Any,
        *,
        default_kw_only: bool,
) -> BuiltStdField:
    default: ta.Any = getattr(cls, a_name, dc.MISSING)
    if isinstance(default, dc.Field):
        f = default
    else:
        if isinstance(default, types.MemberDescriptorType):
            # This is a field in __slots__, so it has no default value.
            default = dc.MISSING
        f = dc.field(default=default)

    attr_sets: dict[str, ta.Any] = dict(
        name=a_name,
        type=a_type,
    )

    # field type

    ft = StdFieldType.INSTANCE
    if std_is_classvar(cls, f.type):
        ft = StdFieldType.CLASS_VAR
    if std_is_initvar(cls, f.type):
        ft = StdFieldType.INIT_VAR
    if ft in (StdFieldType.CLASS_VAR, StdFieldType.INIT_VAR):
        if f.default_factory is not dc.MISSING:
            raise TypeError(f'field {a_name} cannot have a default factory')
    attr_sets.update(_field_type=ft.value)

    # kw_only

    if ft in (StdFieldType.INSTANCE, StdFieldType.INIT_VAR):
        if f.kw_only is dc.MISSING:
            attr_sets.update(kw_only=default_kw_only)
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

    return BuiltStdField(
        f,
        a_name,
        a_type,
        attr_mods=AttrMods(f, sets=attr_sets) if attr_sets else None,
    )


##


@dc.dataclass(frozen=True)
class BuiltClsStdFields:
    fields: ta.Mapping[str, dc.Field]

    _: dc.KW_ONLY

    attr_mods: ta.Sequence[AttrMods] | None = None


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

    built_fields: list[BuiltStdField] = []
    attr_mods: list[AttrMods] = []

    kw_only_seen = False
    for name, ann in cls_annotations.items():
        if std_is_kw_only(cls, ann):
            if kw_only_seen:
                raise TypeError(f'{name!r} is KW_ONLY, but KW_ONLY has already been specified')
            kw_only_seen = True
            kw_only = True

        else:
            bsf = build_std_field(
                cls,
                name,
                ann,
                default_kw_only=kw_only,
            )
            built_fields.append(bsf)
            if (fam := bsf.attr_mods) is not None:
                attr_mods.append(fam)

    cls_attr_sets: dict[str, ta.Any] = {}
    cls_attr_dels: set[str] = set()
    for bsf in built_fields:
        fields[bsf.name] = bsf.fld
        if isinstance(getattr(cls, bsf.name, None), dc.Field):
            if bsf.fld.default is dc.MISSING:
                cls_attr_dels.add(bsf.name)
            else:
                cls_attr_sets[bsf.name] = bsf.fld.default

    for name, value in cls.__dict__.items():
        if isinstance(value, dc.Field) and name not in cls_annotations:
            raise TypeError(f'{name!r} is a field but has no type annotation')

    if cls_attr_sets or cls_attr_dels:
        attr_mods.append(AttrMods(
            cls,
            sets=cls_attr_sets,
            dels=cls_attr_dels,  # noqa
        ))

    return BuiltClsStdFields(
        fields,
        attr_mods=attr_mods,
    )


def install_built_cls_std_fields(
        cls: type,
        csf: BuiltClsStdFields,
) -> None:
    for am in csf.attr_mods or []:
        am.apply()

    setattr(cls, STD_FIELDS_ATTR, csf.fields)


##


def build_std_field_metadata_update(
        f: dc.Field,
        metadata: ta.Mapping[str, ta.Mapping[ta.Any, ta.Any]],
) -> AttrMods | None:
    md: ta.Any = f.metadata

    mdu: dict = {}
    for k, v in metadata.items():
        if md is None or md.get(k) != v:
            mdu[k] = v  # noqa
    if not mdu:
        return None

    if md is None:
        md = mdu
    else:
        md = collections.ChainMap(mdu, md)
    md = types.MappingProxyType(md)

    return AttrMods(f, sets=dict(metadata=md))
