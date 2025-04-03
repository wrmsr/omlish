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
        super().__init__()

        tmp: list = []
        udct: dict = {}
        for tv in tvs:
            if isinstance(tv, UniqueTypedValue):
                uoc = tv._unique_typed_value_cls  # noqa
                if not override:
                    try:
                        exu = udct[uoc]
                    except KeyError:
                        pass
                    else:
                        raise DuplicateUniqueTypedValueError(uoc, tv, check.single(exu))
                ulst = udct.setdefault(uoc, [])
                ulst.append(tv)
                tmp.append((tv, len(ulst)))
            elif isinstance(tv, TypedValue):
                tmp.append(tv)
            else:
                raise TypeError(tv)

        lst: list = []
        dct: dict = {}
        for tv in tmp:
            if isinstance(tv, tuple):
                uo, idx = tv  # type: ignore
                ulst = udct[uo._unique_typed_value_cls]  # noqa
                if idx == len(ulst):
                    lst.append(uo)
                    dct[uo._unique_typed_value_cls] = uo  # noqa
                    dct[type(uo)] = uo
            else:
                lst.append(tv)
                dct.setdefault(type(tv), []).append(tv)

        self._lst = lst
        self._dct = dct

        self._any_dct: dict[type, ta.Sequence[ta.Any]] = {}

    def without(self, *tys: type) -> ta.Iterator[TypedValueT]:
        for o in self._lst:
            if not isinstance(o, tys):
                yield o

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
