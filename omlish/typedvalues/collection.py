import typing as ta

from .. import check
from .. import dataclasses as dc
from .. import lang
from .accessor import TypedValuesAccessor
from .values import TypedValue
from .values import UniqueTypedValue


TypedValueT = ta.TypeVar('TypedValueT', bound='TypedValue')

UniqueTypedValueT = ta.TypeVar('UniqueTypedValueT', bound='UniqueTypedValue')


##


@dc.dataclass()
class DuplicateUniqueTypedValueError(Exception, ta.Generic[UniqueTypedValueT]):
    cls: type[UniqueTypedValueT]
    new: UniqueTypedValueT
    old: UniqueTypedValueT


class TypedValues(
    TypedValuesAccessor[TypedValueT],
    lang.Final,
    ta.Generic[TypedValueT],
):
    def __init__(self, *tvs: TypedValueT, override: bool = False) -> None:
        if hasattr(self, '_lst'):
            # When __new__ returns the empty singleton __init__ will still be called.
            return

        super().__init__()

        tmp: list = []
        udct: dict = {}
        for tv in tvs:
            if isinstance(tv, UniqueTypedValue):
                utvc = tv._unique_typed_value_cls  # noqa
                if not override:
                    try:
                        exu = udct[utvc]
                    except KeyError:
                        pass
                    else:
                        raise DuplicateUniqueTypedValueError(utvc, tv, check.single(exu))
                ulst = udct.setdefault(utvc, [])
                ulst.append(tv)
                tmp.append((utvc, tv, ulst, len(ulst)))
            elif isinstance(tv, TypedValue):
                tmp.append(tv)
            else:
                raise TypeError(tv)

        lst: list = []
        dct: dict = {}
        for obj in tmp:
            if isinstance(obj, tuple):
                utvc, tv, ulst, idx = obj
                if idx == len(ulst):
                    lst.append(tv)
                    dct[utvc] = tv
                    dct[type(tv)] = tv
            else:
                tv = obj
                lst.append(tv)
                dct.setdefault(type(tv), []).append(tv)

        self._lst = lst
        self._dct = dct

        self._any_dct: dict[type, ta.Sequence[ta.Any]] = {}

    #

    _EMPTY: ta.ClassVar['TypedValues']

    @classmethod
    def empty(cls) -> 'TypedValues':
        return cls._EMPTY

    def __new__(cls, *tvs, **kwargs):  # noqa
        if not tvs:
            try:
                return cls._EMPTY
            except AttributeError:
                pass
        return super().__new__(cls)

    #

    def with_(self, *tvs, override: bool = False) -> 'TypedValues':
        return TypedValues(*self._lst, *tvs, override=override)

    def without(self, *tys: type) -> ta.Iterator[TypedValueT]:
        for o in self._lst:
            if isinstance(o, tys):
                continue
            yield o

    #

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({", ".join(map(repr, self._lst))})'

    #

    def __iter__(self) -> ta.Iterator[TypedValueT]:
        return iter(self._lst)

    def __len__(self) -> int:
        return len(self._lst)

    def __bool__(self) -> bool:
        return bool(self._lst)

    #

    def _typed_value_contains(self, cls):
        return cls in self._dct

    def _typed_value_getitem(self, key):
        if isinstance(key, int):
            return self._lst[key]
        elif isinstance(key, type):
            return self._dct[check.issubclass(key, TypedValue)]
        else:
            raise TypeError(key)

    def _typed_value_get(self, key, /, default=None):
        check.issubclass(key, TypedValue)
        try:
            return self._dct[key]
        except KeyError:
            if issubclass(key, UniqueTypedValue):
                return default
            elif default is not None:
                return list(default)
            else:
                return []

    def _typed_value_get_any(self, cls):
        try:
            return self._any_dct[cls]
        except KeyError:
            pass
        ret = [tv for tv in self if isinstance(tv, cls)]
        self._any_dct[cls] = ret
        return ret


TypedValues._EMPTY = TypedValues()  # noqa
