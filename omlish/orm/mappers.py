# ruff: noqa: SLF001
import typing as ta

from .. import check
from .. import collections as col
from .fields import Field
from .fields import KeyField
from .fields import RefField
from .indexes import Index
from .keys import _KEY_TYPES
from .keys import Key
from .keys import _AutoKey
from .keys import _Key
from .refs import _REF_TYPES
from .refs import _LazyRef
from .snaps import Snap


if ta.TYPE_CHECKING:
    from .registries import Registry


K = ta.TypeVar('K')
T = ta.TypeVar('T')


##


class Mapper(ta.Generic[K, T]):
    def __init__(
            self,
            cls: type[T],
            store_name: str,
            fields: ta.Sequence[Field],
            *,
            indexes: ta.Sequence[Index] | None = None,
    ) -> None:
        super().__init__()

        check.isinstance(cls, type)
        self._cls = cls
        self._store_name = check.non_empty_str(store_name)

        self._fields = fields = check.not_empty(list(fields))
        self._indexes = indexes = list(indexes) if indexes is not None else []

        for f in fields:
            f._set_mapper(self)
        for idx in indexes:
            idx._set_mapper(self)

        self._fields_by_name: ta.Mapping[str, Field] = col.make_map(((f.name, f) for f in fields), strict=True)
        self._fields_by_store_name: ta.Mapping[str, Field] = col.make_map(((f.store_name, f) for f in fields), strict=True)  # noqa
        self._store_name_by_field_name = {f.name: f.store_name for f in fields}

        self._key_field: KeyField = check.single(f for f in fields if f.__class__ is KeyField)  # type: ignore[assignment]  # noqa
        self._ref_fields: ta.Sequence[RefField] = [f for f in fields if f.__class__ is RefField]  # type: ignore[misc]

        self._indexes_by_store_name: ta.Mapping[str, Index] = col.make_map((
            (check.non_empty_str(idx.store_name), idx) for idx in indexes
        ), strict=True)
        self._index_field_store_names: ta.Mapping[Index, tuple[str, ...]] = {
            idx: tuple(self._fields_by_name[f].store_name for f in idx.fields)
            for idx in indexes
        }

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
    def ref_fields(self) -> ta.Sequence[RefField]:
        return self._ref_fields

    @property
    def indexes_by_store_name(self) -> ta.Mapping[str, Index]:
        return self._indexes_by_store_name

    @property
    def index_field_store_names(self) -> ta.Mapping[Index, tuple[str, ...]]:
        return self._index_field_store_names

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

    def key_for_obj(self, obj: T) -> Key[K]:
        return check.isinstance(getattr(obj, self.key_field.name), Key)

    def key_for_snap(self, snap: Snap) -> Key[K]:
        k = snap[self._key_field._name]
        kt = k.__class__
        if kt is _AutoKey:
            return k
        check.not_in(kt, _KEY_TYPES)
        return _Key(k)

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

        elif ft is RefField:
            if f._optional and v is None:  # type: ignore[attr-defined]
                pass
            else:
                check.state(vr)
                v = v.k
                if v.__class__ is _AutoKey:
                    pass
                else:
                    v = v.k

        else:
            check.state(not vk)
            check.state(not vr)

            if (co := self._registry._codec) is not None:
                v = co.decode(v, f._rty)

        return v

    def obj_to_snap(self, obj: T) -> Snap:
        dct: dict[str, ta.Any] = {}

        for f in self._fields:
            dct[f._store_name] = self.field_value_to_snap_value(f, getattr(obj, f.name))

        return dct

    #

    def snap_value_to_field_value(self, f: Field, v: ta.Any) -> ta.Any:
        ft = f.__class__
        if ft is KeyField:
            v = _Key(v)

        elif ft is RefField:
            if v is None:
                check.state(f._optional)  # type: ignore[attr-defined]
            else:
                v = _LazyRef(f._ref_obj_cls, _Key(v))  # type: ignore[attr-defined]

        elif (co := self._registry._codec) is not None:
            v = co.decode(v, f._rty)

        return v

    def snap_to_obj(self, snap: Snap) -> T:
        check.equal(len(snap), len(self._fields))

        kw: dict[str, ta.Any] = {}

        for f in self._fields:
            kw[f._name] = self.snap_value_to_field_value(f, snap[f._store_name])

        return self._cls(**kw)
