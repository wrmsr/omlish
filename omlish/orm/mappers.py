# ruff: noqa: SLF001
import typing as ta

from .. import check
from .. import collections as col
from .. import typedvalues as tv
from .backrefs import Backref
from .codecs import FieldCodec
from .fields import Field
from .fields import FieldOption
from .fields import KeyField
from .fields import RefField
from .indexes import Index
from .keys import _KEY_TYPES
from .keys import Key
from .keys import _AutoKey
from .keys import _ValKey
from .options import MapperOption
from .refs import _REF_TYPES
from .refs import _KeyRef
from .snaps import Snap
from .timestamps import CreatedAt
from .timestamps import UpdatedAt
from .values import _AutoValue


if ta.TYPE_CHECKING:
    from .registries import Registry


K = ta.TypeVar('K')
T = ta.TypeVar('T')

FieldOptionT = ta.TypeVar('FieldOptionT', bound=FieldOption)


##


class Mapper(ta.Generic[K, T]):
    def __init__(
            self,
            cls: type[T],
            store_name: str,
            fields: ta.Sequence[Field],
            *,
            indexes: ta.Sequence[Index] | None = None,
            backrefs: ta.Sequence[Backref] | None = None,
            options: ta.Sequence[MapperOption] | None = None,
    ) -> None:
        super().__init__()

        check.isinstance(cls, type)
        self._cls = cls
        self._store_name = check.non_empty_str(store_name)

        self._fields = fields = list(fields) if fields is not None else []
        self._indexes = indexes = list(indexes) if indexes is not None else []
        self._backrefs = backrefs = list(backrefs) if backrefs is not None else []

        self._options = tv.TypedValues(*(options or []))

        for f in fields:
            check.isinstance(f, Field)
            f._set_mapper(self)
        for idx in indexes:
            check.isinstance(idx, Index)
            idx._set_mapper(self)
        for br in backrefs:
            check.isinstance(br, Backref)

        self._fields_by_name: ta.Mapping[str, Field] = col.make_map(((f.name, f) for f in fields), strict=True)
        self._fields_by_store_name: ta.Mapping[str, Field] = col.make_map(((f.store_name, f) for f in fields), strict=True)  # noqa
        self._store_name_by_field_name = {f.name: f.store_name for f in fields}

        self._key_field: KeyField = check.single(f for f in fields if f.__class__ is KeyField)  # noqa
        self._key_field_store_name = self._key_field._store_name
        self._ref_fields: ta.Sequence[RefField] = [f for f in fields if f.__class__ is RefField]  # noqa

        self._indexes_by_store_name: ta.Mapping[str, Index] = col.make_map((
            (check.non_empty_str(idx.store_name), idx) for idx in indexes
        ), strict=True)
        self._index_field_store_names: ta.Mapping[Index, tuple[str, ...]] = {
            idx: tuple(self._fields_by_name[f].store_name for f in idx.fields)
            for idx in indexes
        }

        self._created_at_field = self._single_field_with_option(CreatedAt)
        self._created_at_store_name = f2._store_name if (f2 := self._created_at_field) is not None else None
        self._updated_at_field = self._single_field_with_option(UpdatedAt)
        self._updated_at_store_name = f2._store_name if (f2 := self._updated_at_field) is not None else None

        self._auto_value_fields: ta.Sequence[Field] = (
            *filter(None, (
                self._created_at_field,
                self._updated_at_field,
            )),
        )

    def __repr__(self) -> str:
        return f'{type(self).__name__}({self._cls!r}, {self._store_name!r})'

    @property
    def cls(self) -> type[T]:
        return self._cls

    @property
    def store_name(self) -> str:
        return self._store_name

    @property
    def fields(self) -> ta.Sequence[Field]:
        return self._fields

    @property
    def indexes(self) -> ta.Sequence[Index]:
        return self._indexes

    @property
    def backrefs(self) -> ta.Sequence[Backref]:
        return self._backrefs

    @property
    def options(self) -> tv.TypedValues[MapperOption]:
        return self._options

    #

    _registry: 'Registry'

    def _set_registry(self, r: 'Registry') -> None:
        try:
            self._registry  # noqa
        except AttributeError:
            pass
        else:
            raise RuntimeError('registry already set')
        self._registry = r

    @property
    def registry(self) -> 'Registry':
        return self._registry

    #

    @property
    def fields_by_name(self) -> ta.Mapping[str, Field]:
        return self._fields_by_name

    @property
    def fields_by_store_name(self) -> ta.Mapping[str, Field]:
        return self._fields_by_store_name

    @property
    def store_name_by_field_name(self) -> ta.Mapping[str, str]:
        return self._store_name_by_field_name

    @property
    def key_field(self) -> KeyField:
        return self._key_field

    @property
    def key_field_store_name(self) -> str:
        return self._key_field_store_name

    @property
    def ref_fields(self) -> ta.Sequence[RefField]:
        return self._ref_fields

    @property
    def indexes_by_store_name(self) -> ta.Mapping[str, Index]:
        return self._indexes_by_store_name

    @property
    def index_field_store_names(self) -> ta.Mapping[Index, tuple[str, ...]]:
        return self._index_field_store_names

    def _single_field_with_option(self, opt_cls: type[FieldOptionT]) -> Field | None:
        lst = [f for f in self._fields if opt_cls in f.options]
        if not lst:
            return None
        return check.single(lst)

    @property
    def created_at_field(self) -> Field | None:
        return self._created_at_field

    @property
    def created_at_store_name(self) -> str | None:
        return self._created_at_store_name

    @property
    def updated_at_field(self) -> Field | None:
        return self._updated_at_field

    @property
    def updated_at_store_name(self) -> str | None:
        return self._updated_at_store_name

    @property
    def auto_value_fields(self) -> ta.Sequence[Field]:
        return self._auto_value_fields

    #

    def key_for_obj(self, obj: T) -> Key[K]:
        return check.isinstance(getattr(obj, self.key_field.name), Key)

    def key_for_snap(self, snap: Snap) -> Key[K]:
        k = snap[self._key_field._name]
        kt = k.__class__
        if kt is _AutoKey:
            return k
        check.not_in(kt, _KEY_TYPES)
        return _ValKey(k)

    #

    def field_value_to_snap_value(self, f: Field, v: ta.Any) -> ta.Any:
        vt = v.__class__
        vk = vt in _KEY_TYPES
        vr = vt in _REF_TYPES

        ft = f.__class__
        if ft is KeyField:
            check.state(vk)
            if vt is _AutoKey:
                pass
            else:
                v = v.k
                vt = v.__class__

        elif ft is RefField:
            if f._optional and v is None:  # type: ignore[attr-defined]
                pass
            else:
                check.state(vr)
                v = v.k
                vt = v.__class__
                if vt is _AutoKey:
                    pass
                else:
                    v = v.k
                    vt = v.__class__

        else:
            check.state(not vk)
            check.state(not vr)

            if (co := f._options.get(FieldCodec, None)) is not None:
                v = co.v.encode(v, f.unwrapped_rty)
                vt = v.__class__

        if vt is _AutoValue:
            raise TypeError(v)

        return v

    def obj_to_snap(self, obj: T) -> Snap:
        dct: dict[str, ta.Any] = {}

        for f in self._fields:
            v = getattr(obj, f.name)
            vt = v.__class__

            if vt is _AutoValue:
                continue

            dct[f._store_name] = self.field_value_to_snap_value(f, v)

        return dct

    #

    def snap_value_to_field_value(self, f: Field, v: ta.Any) -> ta.Any:
        ft = f.__class__
        if ft is KeyField:
            v = _ValKey(v)

        elif ft is RefField:
            if v is None:
                check.state(f._optional)  # type: ignore[attr-defined]
            else:
                v = _KeyRef(f._ref_obj_cls, _ValKey(v))  # type: ignore[attr-defined]

        elif (co := f._options.get(FieldCodec, None)) is not None:
            v = co.v.decode(v, f.unwrapped_rty)

        return v

    def snap_to_obj(self, snap: Snap) -> T:
        check.equal(len(snap), len(self._fields))

        kw: dict[str, ta.Any] = {}

        for f in self._fields:
            kw[f._name] = self.snap_value_to_field_value(f, snap[f._store_name])

        return self._cls(**kw)
