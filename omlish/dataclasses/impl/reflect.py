import dataclasses as dc
import inspect
import sys
import typing as ta

from ... import cached
from ... import check
from ... import lang
from ... import reflect as rfl
from .internals import FIELDS_ATTR
from .internals import Params
from .internals import is_kw_only
from .metadata import METADATA_ATTR
from .metadata import Metadata
from .metadata import get_merged_metadata
from .params import PARAMS_ATTR
from .params import Params12
from .params import ParamsExtras
from .params import get_params
from .params import get_params12
from .params import get_params_extras
from .utils import Namespace


MISSING = dc.MISSING


class ClassInfo:

    def __init__(self, cls: type) -> None:
        check.isinstance(cls, type)
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
    def cls_annotations(self) -> dict[str, ta.Any]:
        return inspect.get_annotations(self._cls)

    @cached.property
    def params(self) -> Params:
        return get_params(self._cls)

    @cached.property
    def cls_params(self) -> Params | None:
        return self._cls.__dict__.get(PARAMS_ATTR)

    @cached.property
    def params12(self) -> Params12:
        return get_params12(self._cls)

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

    class _FoundFields(ta.NamedTuple):
        fields: dict[str, dc.Field]
        field_owners: dict[str, type]

    @lang.cached_nullary
    def _find_fields(self) -> _FoundFields:
        fields: dict[str, dc.Field] = {}
        field_owners: dict[str, type] = {}

        for b in self._cls.__mro__[-1:0:-1]:
            base_fields = getattr(b, FIELDS_ATTR, None)
            if base_fields is not None:
                for f in base_fields.values():
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
    def field_owners(self) -> ta.Mapping[str, type]:
        return self._find_fields().field_owners

    @cached.property
    def generic_mro(self) -> ta.Sequence[rfl.Type]:
        return rfl.generic_mro(self._cls)

    @cached.property
    def mro_type_args(self) -> ta.Mapping[type, ta.Mapping[ta.TypeVar, rfl.Type]]:
        ret: dict[type, ta.Mapping[ta.TypeVar, rfl.Type]] = {}
        for bt in self.generic_mro:
            if isinstance(bt, rfl.Generic):
                if bt.cls in ret:
                    raise TypeError(f'duplicate generic mro entry: {bt!r}')
                ret[bt.cls] = rfl.get_type_var_replacements(bt)
        return ret


def reflect(obj: ta.Any) -> ClassInfo:
    cls = obj if isinstance(obj, type) else type(obj)
    return ClassInfo(cls)
