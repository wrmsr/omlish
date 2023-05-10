import dataclasses as dc
import types
import typing as ta

from .. import properties
from .internals import FIELDS
from .internals import FieldType
from .internals import get_field
from .internals import get_field_type
from .types import ExtraFieldParams


class Fields(ta.Sequence[dc.Field]):

    def __init__(self, fields: ta.Iterable[dc.Field]) -> None:
        super().__init__()

        self._seq = tuple(fields)

        by_name = {}
        for fld in self._seq:
            if fld.name in by_name:
                raise NameError(fld.name)
            by_name[fld.name] = fld
        self._by_name = types.MappingProxyType(by_name)

    @property
    def all(self) -> ta.Sequence[dc.Field]:
        return self._seq

    def __getitem__(self, item: ta.Union[int, slice, str]) -> dc.Field:
        if isinstance(item, (int, slice)):
            return self._seq[item]
        elif isinstance(item, str):
            return self._by_name[item]
        else:
            raise TypeError(item)

    def __contains__(self, item: ta.Union[dc.Field, str]) -> bool:
        if isinstance(item, dc.Field):
            return item in self._seq
        elif isinstance(item, str):
            return item in self._by_name
        else:
            raise TypeError(item)

    def __len__(self) -> int:
        return len(self._seq)

    def __iter__(self) -> ta.Iterable[dc.Field]:
        return iter(self._seq)

    @properties.cached
    @property
    def by_name(self) -> ta.Mapping[str, dc.Field]:
        return self._by_name

    @properties.cached
    @property
    def by_field_type(self) -> ta.Mapping[FieldType, ta.Sequence[dc.Field]]:
        ret = {}
        for f in self:
            ret.setdefault(get_field_type(f), []).append(f)
        return types.MappingProxyType({k: list(v) for k, v in ret.items()})

    @properties.cached
    @property
    def instance(self) -> ta.Sequence[dc.Field]:
        return self.by_field_type.get(FieldType.INSTANCE, ())

    @properties.cached
    @property
    def init(self) -> ta.List[dc.Field]:
        return [f for f in self if get_field_type(f) in (FieldType.INSTANCE, FieldType.INIT)]


def _has_default(fld: dc.Field) -> bool:
    return fld.default is not dc.MISSING or fld.default_factory is not dc.MISSING


def build_cls_fields(
        cls: type,
        *,
        reorder: bool = False,
        install: bool = False,
) -> Fields:
    fields = {}
    dc_mro = [b for b in reversed(cls.__mro__) if getattr(b, FIELDS, None)]
    for b in dc_mro:
        base_fields = getattr(b, FIELDS, None)
        if base_fields:
            for f in base_fields.values():
                fields[f.name] = f

    # Annotations that are defined in this class (not in base classes). If __annotations__ isn't present, then this
    # class adds no new annotations. We use this to compute fields that are added by this class.
    #
    # Fields are found from cls_annotations, which is guaranteed to be ordered. Default values are from class
    # attributes, if a field has a default. If the default value is a Field(), then it contains additional info # beyond
    # (and possibly including) the actual default value. Pseudo-fields ClassVars and InitVars are included, despite the
    # fact that they're not real fields. That's dealt with later.
    cls_annotations = cls.__dict__.get('__annotations__', {})

    # Now find fields in our class. While doing so, validate some things, and set the default values (as class
    # attributes) where we can.
    cls_fields = [get_field(cls, name, type) for name, type in cls_annotations.items()]
    for f in cls_fields:
        fields[f.name] = f

        if install:
            # If the class attribute (which is the default value for this field) exists and is of type 'Field', replace
            # it with the real default. This is so that normal class introspection sees a real default value, not a
            # Field.
            if isinstance(getattr(cls, f.name, None), dc.Field):
                if f.default is dc.MISSING:
                    # If there's no default, delete the class attribute. This happens if we specify field(repr=False),
                    # for example (that is, we specified a field object, but no default value). Also if we're using a
                    # default factory. The class attribute should not be set at all in the post-processed class.
                    delattr(cls, f.name)
                else:
                    setattr(cls, f.name, f.default)

    # Do we have any Field members that don't also have annotations?
    for name, value in cls.__dict__.items():
        if isinstance(value, dc.Field) and name not in cls_annotations:
            raise TypeError(f'{name!r} is a field but has no type annotation')

    if reorder:
        reordered = {}
        for hd in [False, True]:
            for kwo in [False, True]:
                for k, v in fields.items():
                    if _has_default(v) != hd:
                        continue
                    efp = v.metadata.get(ExtraFieldParams)
                    if (efp.kwonly if efp is not None else False) != kwo:
                        continue
                    reordered[k] = v
        if set(fields) != set(reordered):
            raise KeyError(fields, reordered)
        fields = reordered

    if install:
        setattr(cls, FIELDS, dict(fields))

    return Fields(fields.values())
