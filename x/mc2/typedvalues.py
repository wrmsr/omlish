import typing as ta

from omlish import check
from omlish import dataclasses as dc
from omlish import lang
from omlish import reflect as rfl


T = ta.TypeVar('T')
TypedValueT = ta.TypeVar('TypedValueT', bound='TypedValue')
TypedValueU = ta.TypeVar('TypedValueU', bound='TypedValue')
UniqueTypedValueU = ta.TypeVar('UniqueTypedValueU', bound='UniqueTypedValue')


##


class TypedValue(lang.Abstract):
    pass


class UniqueTypedValue(TypedValue, lang.Abstract):
    unique_tv_cls: ta.ClassVar[type[TypedValue]]

    def __init_subclass__(cls, **kwargs: ta.Any) -> None:
        super().__init_subclass__(**kwargs)

        if UniqueTypedValue in cls.__bases__:
            try:
                cls.unique_tv_cls  # noqa
            except AttributeError:
                cls.unique_tv_cls = cls
            else:
                raise TypeError(f'Class already has unique_tv_cls: {cls}')


@dc.dataclass(frozen=True)
@dc.extra_params(generic_init=True)
class ScalarTypedValue(TypedValue, lang.Abstract, ta.Generic[T]):
    v: T

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.v!r})'


##


@dc.dataclass()
class DuplicateUniqueTypedValueError(Exception, ta.Generic[UniqueTypedValueU]):
    cls: type[UniqueTypedValueU]
    new: UniqueTypedValueU
    old: UniqueTypedValueU


class TypedValues(lang.Final, ta.Generic[TypedValueT]):
    def __init__(self, *tvs: TypedValueT, override: bool = False) -> None:
        super().__init__()

        tmp: list = []
        udct: dict = {}
        for tv in tvs:
            if isinstance(tv, UniqueTypedValue):
                uoc = tv.unique_tv_cls
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
                ulst = udct[uo.unique_tv_cls]
                if idx == len(ulst):
                    lst.append(uo)
                    dct[uo.unique_tv_cls] = uo
                    dct[type(uo)] = uo
            else:
                lst.append(tv)
                dct.setdefault(type(tv), []).append(tv)

        self._lst = lst
        self._dct = dct

    def without(self, *tys: type) -> ta.Iterator[TypedValueT]:
        for o in self._lst:
            if not isinstance(o, tys):
                yield o

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({", ".join(map(repr, self._lst))})'

    def __iter__(self) -> ta.Iterator[TypedValueT]:
        return iter(self._lst)

    def __len__(self) -> int:
        return len(self._lst)

    def __contains__(self, cls: type[TypedValueU]) -> bool:
        return cls in self._dct

    def __bool__(self) -> bool:
        return bool(self._lst)

    @ta.overload
    def __getitem__(self, idx: int) -> TypedValueT:
        ...

    @ta.overload
    def __getitem__(self, cls: type[UniqueTypedValueU]) -> UniqueTypedValueU:  # type: ignore[overload-overlap]
        ...

    @ta.overload
    def __getitem__(self, cls: type[TypedValueU]) -> ta.Sequence[TypedValueU]:
        ...

    def __getitem__(self, key):
        if isinstance(key, int):
            return self._lst[key]
        else:
            return self._dct[key]


##


class TypedValueGeneric(ta.Generic[TypedValueT], lang.Abstract):
    _typed_value_type: ta.ClassVar[rfl.TypeInfo]

    def __init_subclass__(cls, **kwargs: ta.Any) -> None:
        super().__init_subclass__(**kwargs)

        if (
                TypedValueGeneric not in cls.__bases__ or
                '_typed_value_type' in cls.__dict__
        ):
            return

        g_mro = rfl.ALIAS_UPDATING_GENERIC_SUBSTITUTION.generic_mro(cls)
        g_tvg = check.single(
            gb
            for gb in g_mro
            if isinstance(gb, rfl.Generic) and gb.cls is TypedValueGeneric
        )
        tvt = check.single(g_tvg.args)
        cls._typed_value_type = tvt
