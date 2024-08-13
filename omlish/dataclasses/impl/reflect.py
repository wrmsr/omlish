"""
TODO:
 - more cache-recursive reuse - fields, mro, etc
"""
import dataclasses as dc
import inspect
import sys
import typing as ta
import weakref

from ... import cached
from ... import check
from ... import collections as col
from ... import lang
from ... import reflect as rfl
from .fields import field_type
from .internals import FIELDS_ATTR
from .internals import FieldType
from .internals import Params
from .internals import is_kw_only
from .metadata import METADATA_ATTR
from .metadata import Metadata
from .metadata import get_merged_metadata
from .params import PARAMS_ATTR
from .params import ParamsExtras
from .params import get_params
from .params import get_params_extras
from .utils import Namespace


try:
    import annotationlib  # noqa
except ImportError:
    annotationlib = None


MISSING = dc.MISSING


def _get_annotations(obj):
    if annotationlib is not None:
        return annotationlib.get_annotations(obj, format=annotationlib.Format.FORWARDREF)  # noqa
    else:
        return inspect.get_annotations(obj)


class ClassInfo:

    def __init__(self, cls: type, *, _constructing: bool = False) -> None:
        check.isinstance(cls, type)
        self._constructing = _constructing
        if not _constructing:
            check.arg(dc.is_dataclass(cls))
        super().__init__()
        self._cls: type = cls

    @property
    def cls(self) -> type:
        return self._cls  # noqa

    @cached.property
    def globals(self) -> Namespace:
        if self._cls.__module__ in sys.modules:
            return sys.modules[self._cls.__module__].__dict__
        else:
            return {}

    @cached.property
    def cls_annotations(self) -> ta.Mapping[str, ta.Any]:
        return _get_annotations(self._cls)

    ##

    @cached.property
    def params(self) -> Params:
        return get_params(self._cls)

    @cached.property
    def cls_params(self) -> Params | None:
        return self._cls.__dict__.get(PARAMS_ATTR)

    @cached.property
    def params_extras(self) -> ParamsExtras:
        return get_params_extras(self._cls)

    @cached.property
    def cls_params_extras(self) -> ParamsExtras | None:
        return (self.cls_metadata or {}).get(ParamsExtras)

    @cached.property
    def cls_metadata(self) -> Metadata | None:
        return self._cls.__dict__.get(METADATA_ATTR)

    @cached.property
    def merged_metadata(self) -> Metadata:
        return get_merged_metadata(self._cls)

    ##

    class _FoundFields(ta.NamedTuple):
        fields: dict[str, dc.Field]
        field_owners: dict[str, type]

    @lang.cached_function
    def _find_fields(self) -> _FoundFields:
        if self._constructing:
            check.in_(FIELDS_ATTR, self._cls.__dict__)

        fields: dict[str, dc.Field] = {}
        field_owners: dict[str, type] = {}

        for b in self._cls.__mro__[-1:0:-1]:
            base_fields = getattr(b, FIELDS_ATTR, None)
            if base_fields is not None:
                for name in reflect(b).cls_annotations:
                    try:
                        f = base_fields[name]
                    except KeyError:
                        continue
                    fields[f.name] = f
                    field_owners[f.name] = b

        cls_fields = getattr(self._cls, FIELDS_ATTR)
        for name, ann in self.cls_annotations.items():
            if is_kw_only(self._cls, ann):
                continue
            fields[name] = cls_fields[name]
            field_owners[name] = self._cls

        return ClassInfo._FoundFields(fields, field_owners)

    @cached.property
    def fields(self) -> ta.Mapping[str, dc.Field]:
        return self._find_fields().fields

    @cached.property
    def instance_fields(self) -> ta.Sequence[dc.Field]:
        return [f for f in self.fields.values() if field_type(f) is FieldType.INSTANCE]

    @cached.property
    def field_owners(self) -> ta.Mapping[str, type]:
        return self._find_fields().field_owners

    ##

    @cached.property
    def generic_mro(self) -> ta.Sequence[rfl.Type]:
        return rfl.ALIAS_UPDATING_GENERIC_SUBSTITUTION.generic_mro(self._cls)

    @cached.property
    def generic_mro_lookup(self) -> ta.Mapping[type, rfl.Type]:
        return col.unique_map(((check.not_none(rfl.get_concrete_type(g)), g) for g in self.generic_mro), strict=True)

    @cached.property
    def generic_replaced_field_types(self) -> ta.Mapping[str, rfl.Type]:
        ret: dict[str, ta.Any] = {}
        for f in self.fields.values():
            fo = self.field_owners[f.name]
            go = self.generic_mro_lookup[fo]
            tvr = rfl.get_type_var_replacements(go)
            fty = rfl.type_(f.type)
            rty = rfl.replace_type_vars(fty, tvr, update_aliases=True)
            ret[f.name] = rty
        return ret

    @cached.property
    def generic_replaced_field_annotations(self) -> ta.Mapping[str, ta.Any]:
        return {k: rfl.to_annotation(v) for k, v in self.generic_replaced_field_types.items()}


_CLASS_INFO_CACHE: ta.MutableMapping[type, ClassInfo] = weakref.WeakKeyDictionary()


def reflect(obj: ta.Any) -> ClassInfo:
    cls = obj if isinstance(obj, type) else type(obj)
    try:
        return _CLASS_INFO_CACHE[cls]
    except KeyError:
        _CLASS_INFO_CACHE[cls] = info = ClassInfo(cls)
        return info
