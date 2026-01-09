# ruff: noqa: UP007
"""
TODO:
 - cext _init_typed_values_collection
"""
import typing as ta

from .. import check
from .. import dataclasses as dc
from .. import lang
from .accessor import TypedValuesAccessor
from .consumer import TypedValuesConsumer
from .values import TypedValue
from .values import UniqueTypedValue


TypedValueT = ta.TypeVar('TypedValueT', bound='TypedValue')
TypedValueU = ta.TypeVar('TypedValueU', bound='TypedValue')

UniqueTypedValueT = ta.TypeVar('UniqueTypedValueT', bound='UniqueTypedValue')


##


@dc.dataclass()
class DuplicateUniqueTypedValueError(Exception):
    cls: type
    new: TypedValue
    old: TypedValue


##


def _init_typed_values_collection(
        *tvs: TypedValueT,
        override: bool = False,
        check_type: type | tuple[type, ...] | None = None,
) -> tuple[
    tuple[TypedValueT, ...],
    dict[type[TypedValueT], TypedValueT | tuple[TypedValueT, ...]],
    dict[type[TypedValueT], TypedValueT | tuple[TypedValueT, ...]],
]:
    if not tvs:
        return ((), {}, {})

    # Either a non-unique TypedValue or a tuple of the form (unique_tv_cls, tv, unique_lst, idx_in_unique_lst). Notably,
    # this intermediate list has the 'opposite' form of the returned collections: where the output dicts have a scalar
    # tv for unique types and a sequence of tv's for non-unique types, this has scalar values for non-unique types and a
    # tuple (heterogeneous, however) for unique types.
    tmp_lst: list[ta.Union[
        TypedValueT,
        tuple[
            type,
            TypedValueT,
            list[TypedValueT],
            int,
        ],
    ]] = []

    # When override is False duplicate unique values raises early. When override is True, however, last-in-wins. This
    # could probably rely on dict insertion order preservation and just overwrite in-place, but it's intentionally done
    # explicitly: preservation of tv ordering in all aspects is crucial, and retention of some intermediates eases
    # debugging and error reporting.
    unique_dct: dict[type, list[TypedValueT]] = {}

    for tv in tvs:
        if check_type is not None:
            if not isinstance(tv, check_type):
                raise TypeError(tv)

        if isinstance(tv, UniqueTypedValue):
            unique_tv_cls = tv._unique_typed_value_cls  # noqa

            if not override:
                try:
                    exu = unique_dct[unique_tv_cls]
                except KeyError:
                    pass
                else:
                    raise DuplicateUniqueTypedValueError(unique_tv_cls, tv, exu[0])

            unique_lst = unique_dct.setdefault(unique_tv_cls, [])
            unique_lst.append(tv)

            tmp_lst.append((unique_tv_cls, tv, unique_lst, len(unique_lst)))

        elif isinstance(tv, TypedValue):
            tmp_lst.append(tv)

        else:
            raise TypeError(tv)

    # The output list with input order preserved and absent of overridden uniques.
    lst: list[TypedValueT] = []

    # This dict has the expected form: scalar tv's for unique types, and an accumulating list for non-unique types.
    tmp_dct: dict[type, TypedValueT | list[TypedValueT]] = {}

    for obj in tmp_lst:
        # Unique type
        if isinstance(obj, tuple):
            unique_tv_cls, tv, unique_lst, idx = obj

            # Last-in-wins
            if idx == len(unique_lst):
                lst.append(tv)
                tmp_dct[unique_tv_cls] = tv

        else:
            tv = obj
            lst.append(tv)
            tmp_dct.setdefault(type(tv), []).append(tv)  # type: ignore[union-attr]

    # This is the 'canonical' output dict: scalar tv's for unique types keyed by their unique type, and homogenous
    # tuples of tv's keyed by their instance type for non-unique types.
    dct: dict[type, TypedValueT | tuple[TypedValueT, ...]] = {
        k: tuple(v) if isinstance(v, list) else v
        for k, v in tmp_dct.items()
    }

    # This is the secondary output dict: the contents of previous dict in addition to entries of unique tv's keyed by
    # their instance type. Notably, for unique tv's in which their unique type *is* their instance type (which is
    # perfectly fine) this will squash together duplicate (k, v) pairs, which is also perfectly fine.
    dct2: dict[type, TypedValueT | tuple[TypedValueT, ...]] = {
        **dct,
        **{type(v): v for v in dct.values() if isinstance(v, UniqueTypedValue)},
    }

    return (tuple(lst), dct, dct2)


##


try:
    from . import _collection  # type: ignore
except ImportError:
    pass
else:
    _init_typed_values_collection = _collection.init_typed_values_collection  # noqa


##


@ta.final
class TypedValues(
    TypedValuesAccessor[TypedValueT],
    lang.Final,
    ta.Generic[TypedValueT],
):
    def __init__(
            self,
            *tvs: TypedValueT,
            override: bool = False,
            check_type: type | tuple[type, ...] | None = None,
    ) -> None:
        self._tup, self._dct, self._dct2 = _init_typed_values_collection(*tvs, override=override, check_type=check_type)  # noqa

    _tup: tuple[TypedValueT, ...]

    # For non unique types, a map from tv instance type to a tuple of instances of that type. For unique tv types, a map
    # from tv unique type to the tv for that unique tv type.
    _dct: dict[type[TypedValueT], TypedValueT | tuple[TypedValueT, ...]]

    # The contents of the previous dict in addition to entries from unique tv's keyed by their instance type.
    _dct2: dict[type[TypedValueT], TypedValueT | tuple[TypedValueT, ...]]

    #

    def without(self, *tys: type) -> ta.Iterator[TypedValueT]:
        for o in self._tup:
            if tys and isinstance(o, tys):
                continue
            yield o

    #

    def discard(self, *tys: type) -> 'TypedValues':
        nl = list(self.without(*tys))

        if len(nl) == len(self._tup):
            return self

        return TypedValues(*self.without(*tys))

    def update(
            self,
            *tvs,
            discard: ta.Iterable[type] | None = None,
            override: bool = False,
    ) -> 'TypedValues':
        if not tvs:
            return self

        n = TypedValues(
            *(self.discard(*discard) if discard else self._tup),
            *tvs,
            override=override,
        )

        if lang.seqs_identical(self._tup, n._tup):
            return self

        return n

    #

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({", ".join(map(repr, self._tup))})'

    #

    _set: frozenset[TypedValueT]

    def to_set(self) -> frozenset[TypedValueT]:
        try:
            return self._set
        except AttributeError:
            pass
        s = frozenset(self._tup)
        self._set = s
        return s

    #

    _hash: int

    def __hash__(self) -> int:
        try:
            return self._hash
        except AttributeError:
            pass
        h = hash(self._tup)
        self._hash = h
        return h

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return NotImplemented
        return (
            other is self or
            other._tup == self._tup
        )

    #

    def __iter__(self) -> ta.Iterator[TypedValueT]:
        return iter(self._tup)

    def __len__(self) -> int:
        return len(self._tup)

    def __bool__(self) -> bool:
        return bool(self._tup)

    #

    def keys(self) -> ta.KeysView[type[TypedValueT]]:
        return self._dct.keys()

    def values(self) -> ta.ValuesView[TypedValueT | tuple[TypedValueT, ...]]:
        return self._dct.values()

    def items(self) -> ta.ItemsView[type[TypedValueT], TypedValueT | tuple[TypedValueT, ...]]:
        return self._dct.items()

    #

    def consume(self) -> TypedValuesConsumer[TypedValueT]:
        return TypedValuesConsumer(self._dct.items())

    #

    def _typed_value_contains(self, cls):
        return cls in self._dct2

    def _typed_value_getitem(self, key):
        if isinstance(key, int):
            return self._tup[key]
        elif isinstance(key, type):
            return self._dct2[check.issubclass(key, TypedValue)]
        else:
            raise TypeError(key)

    _any_dct: dict[type | tuple[type, ...], tuple[TypedValueT, ...]]

    def _typed_value_get_any(self, cls):
        try:
            any_dct = self._any_dct
        except AttributeError:
            any_dct = {}
            self._any_dct = any_dct

        try:
            return any_dct[cls]
        except KeyError:
            pass

        ret = tuple(tv for tv in self if isinstance(tv, cls))
        any_dct[cls] = ret
        return ret


collect = TypedValues


def as_collection(src: ta.Sequence[TypedValueT]) -> TypedValues[TypedValueT]:
    if isinstance(src, TypedValues):
        return src
    else:
        return TypedValues(*src)
