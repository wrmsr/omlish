# ruff: noqa: UP006 UP007 UP037 UP045
# @omlish-lite
import typing as ta
import weakref


T = ta.TypeVar('T')
V = ta.TypeVar('V')


##


@ta.final
class TypeMap(ta.Generic[T]):
    def __init__(self, items: ta.Iterable[T] = (), *, override: bool = False) -> None:
        super().__init__()

        lst: ta.List[T] = []
        dct: ta.Dict[type, ta.Any] = {}
        for item in items:
            if (ty := type(item)) in dct:
                if not override:
                    raise ValueError(ty)
            lst.append(item)
            dct[ty] = item
        self._lst = lst
        self._dct = dct

    def __repr__(self) -> str:
        if not self._lst:
            return f'{type(self).__name__}()'
        return f'{type(self).__name__}<{", ".join(type(i).__name__ for i in self._lst)}>'

    @property
    def items(self) -> ta.Sequence[T]:
        return self._lst

    #

    _EMPTY: 'TypeMap'

    @classmethod
    def of(cls, items: ta.Iterable[T]) -> 'TypeMap[T]':
        if isinstance(items, TypeMap):
            return items
        if not items:
            return cls._EMPTY
        return cls(items)

    @classmethod
    def empty(cls) -> 'TypeMap[T]':
        return cls._EMPTY

    #

    def update(
            self,
            items: ta.Iterable[T],
            *,
            override: bool = False,
    ) -> 'TypeMap[T]':
        if not items:
            return self

        return TypeMap(
            (
                *self._lst,
                *items,
            ),
            override=override,
        )

    def __len__(self) -> int:
        return len(self._lst)

    def __iter__(self) -> ta.Iterator[T]:
        return iter(self._lst)

    def __contains__(self, ty: ta.Type[T]) -> bool:
        return ty in self._lst

    def get(self, ty: ta.Type[T]) -> ta.Optional[T]:
        return self._dct.get(ty)

    def __getitem__(self, ty: ta.Type[T]) -> T:
        return self._dct[ty]

    _any_dct: ta.Dict[ta.Union[type, ta.Tuple[type, ...]], ta.Tuple[T, ...]]

    def get_any(self, cls: ta.Union[type, ta.Tuple[type, ...]]) -> ta.Sequence[T]:
        if not self._lst:
            return ()

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


TypeMap._EMPTY = TypeMap()  # noqa


##


@ta.final
class DynamicTypeMap(ta.Generic[V]):
    def __init__(self, items: ta.Iterable[V] = (), *, weak: bool = False) -> None:
        super().__init__()

        self._items = list(items)
        self._weak = bool(weak)

        self._cache: ta.MutableMapping[type, ta.Any] = weakref.WeakKeyDictionary() if weak else {}

    @property
    def items(self) -> ta.Sequence[V]:
        return self._items

    @property
    def is_weak(self) -> bool:
        return self._weak

    def __len__(self) -> int:
        return len(self._items)

    def __iter__(self) -> ta.Iterator[V]:
        return iter(self._items)

    def __getitem__(self, ty: ta.Type[T]) -> ta.Sequence[T]:
        try:
            return self._cache[ty]
        except KeyError:
            ret = []
            for item in self._items:
                if isinstance(item, ty):
                    ret.append(item)
            self._cache[ty] = ret
            return ret
