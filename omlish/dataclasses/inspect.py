import dataclasses as dc
import typing as ta
import weakref

from .. import cached
from .. import check
from .. import collections as col
from .. import lang
from .. import reflect as rfl
from ._internals import STD_FIELDS_ATTR
from ._internals import StdFieldType
from ._internals import std_field_type
from ._internals import std_is_kw_only


ClassAnnotations: ta.TypeAlias = ta.Mapping[str, ta.Any]


##


def _get_cls_annotations(cls: type) -> ClassAnnotations:
    # Does not use ta.get_type_hints because that's what std dataclasses do [1]. Might be worth revisiting? A part
    # of why they don't is to not import typing for efficiency but we don't care about that degree of startup speed.
    # [1]: https://github.com/python/cpython/blob/54c63a32d06cb5f07a66245c375eac7d7efb964a/Lib/dataclasses.py#L985-L986  # noqa
    return rfl.get_annotations(cls)


_CLS_ANNOTATIONS_CACHE: ta.MutableMapping[type, ClassAnnotations] = weakref.WeakKeyDictionary()


def get_cls_annotations(cls: type) -> ClassAnnotations:
    try:
        return _CLS_ANNOTATIONS_CACHE[cls]
    except KeyError:
        pass
    ret = _get_cls_annotations(cls)
    _CLS_ANNOTATIONS_CACHE[cls] = ret
    return ret


##


class FieldsInspection:
    def __init__(
            self,
            cls: type,
            *,
            cls_fields: ta.Mapping[str, dc.Field] | None = None,
    ) -> None:
        super().__init__()

        self._cls = cls

        self._given_cls_fields = cls_fields
        if cls_fields is None:
            cls_fields = getattr(self._cls, STD_FIELDS_ATTR)
        self._cls_fields = cls_fields

    @property
    def cls(self) -> type:
        return self._cls  # noqa

    @property
    def cls_fields(self) -> ta.Mapping[str, dc.Field]:
        return self._cls_fields

    @cached.property
    def cls_annotations(self) -> ta.Mapping[str, ta.Any]:
        return get_cls_annotations(self._cls)

    #

    class _FoundFields(ta.NamedTuple):
        fields: dict[str, dc.Field]
        field_owners: dict[str, type]

    @lang.cached_function(no_wrapper_update=True)
    def _find_fields(self) -> _FoundFields:
        fields: dict[str, dc.Field] = {}
        field_owners: dict[str, type] = {}

        for b in self._cls.__mro__[-1:0:-1]:
            base_fields = getattr(b, STD_FIELDS_ATTR, None)
            if base_fields is not None:
                for name in get_cls_annotations(b):
                    try:
                        f = base_fields[name]
                    except KeyError:
                        continue
                    fields[f.name] = f
                    field_owners[f.name] = b

        cls_fields = self._cls_fields
        for name, ann in self.cls_annotations.items():
            if std_is_kw_only(self._cls, ann):
                continue
            fields[name] = cls_fields[name]
            field_owners[name] = self._cls

        return FieldsInspection._FoundFields(fields, field_owners)

    @cached.property
    def fields(self) -> ta.Mapping[str, dc.Field]:
        return self._find_fields().fields

    @cached.property
    def instance_fields(self) -> ta.Sequence[dc.Field]:
        return [f for f in self.fields.values() if std_field_type(f) is StdFieldType.INSTANCE]

    @cached.property
    def field_owners(self) -> ta.Mapping[str, type]:
        return self._find_fields().field_owners

    ##

    @cached.property
    def generic_mro(self) -> ta.Sequence[rfl.Type]:
        return rfl.ALIAS_UPDATING_GENERIC_SUBSTITUTION.generic_mro(self._cls)

    @cached.property
    def generic_mro_lookup(self) -> ta.Mapping[type, rfl.Type]:
        return col.make_map(((check.not_none(rfl.get_concrete_type(g)), g) for g in self.generic_mro), strict=True)

    def generic_replaced_field_type(self, fn: str) -> rfl.Type:
        f = self.fields[fn]
        fo = self.field_owners[f.name]
        go = self.generic_mro_lookup[fo]
        tvr = rfl.get_type_var_replacements(go)
        fty = rfl.type_(f.type)
        rty = rfl.replace_type_vars(fty, tvr, update_aliases=True)
        return rty

    @cached.property
    def generic_replaced_field_types(self) -> ta.Mapping[str, rfl.Type]:
        ret: dict[str, ta.Any] = {}
        for f in self.fields.values():
            ret[f.name] = self.generic_replaced_field_type(f.name)
        return ret

    @cached.property
    def generic_replaced_field_annotations(self) -> ta.Mapping[str, ta.Any]:
        return {k: rfl.to_annotation(v) for k, v in self.generic_replaced_field_types.items()}


def inspect_fields(cls: type) -> FieldsInspection:
    return FieldsInspection(cls)
