"""
TODO:
 - -> omlish.collections?
  - potential circ-dep w/ om.dc, but will proxy_init anyway
 - Accessor inputs/outputs should be subtype of class generic param
"""
import abc
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
    _unique_typed_value_cls: ta.ClassVar[type[TypedValue]]

    def __init_subclass__(cls, **kwargs: ta.Any) -> None:
        super().__init_subclass__(**kwargs)

        if UniqueTypedValue in cls.__bases__:
            try:
                cls._unique_typed_value_cls  # noqa
            except AttributeError:
                cls._unique_typed_value_cls = cls
            else:
                raise TypeError(f'Class already has _unique_typed_value_cls: {cls}')


@dc.dataclass(frozen=True)
@dc.extra_params(generic_init=True)
class ScalarTypedValue(TypedValue, lang.Abstract, ta.Generic[T]):
    v: T

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.v!r})'


##


class TypedValuesAccessor(lang.Abstract, ta.Generic[TypedValueT]):
    @ta.final
    def __contains__(self, cls: type[TypedValueU]) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    def _typed_value_contains(self, cls):
        raise NotImplementedError

    #

    @ta.overload
    def __getitem__(self, idx: int) -> TypedValueT:
        ...

    @ta.overload
    def __getitem__(self, cls: type[UniqueTypedValueU]) -> UniqueTypedValueU:  # type: ignore[overload-overlap]
        ...

    @ta.overload
    def __getitem__(self, cls: type[TypedValueU]) -> ta.Sequence[TypedValueU]:
        ...

    @ta.final
    def __getitem__(self, key):
        return self._typed_value_getitem(key)

    @abc.abstractmethod
    def _typed_value_getitem(self, key):
        raise NotImplementedError

    #

    @ta.overload
    def get(
            self,
            tv: UniqueTypedValueU,
    ) -> UniqueTypedValueU:
        ...

    @ta.overload
    def get(
            self,
            cls: type[UniqueTypedValueU],
            /,
            default: UniqueTypedValueU,
    ) -> UniqueTypedValueU:
        ...

    @ta.overload
    def get(  # type: ignore[overload-overlap]
            self,
            cls: type[UniqueTypedValueU],
            /,
            default: None = None,
    ) -> UniqueTypedValueU | None:
        ...

    @ta.overload
    def get(
            self,
            cls: type[TypedValueU],
            /,
            default: ta.Iterable[TypedValueU] | None = None,
    ) -> ta.Sequence[TypedValueU]:
        ...

    @ta.final
    def get(self, key, /, default=None):
        return self._typed_value_get(key, default)

    @abc.abstractmethod
    def _typed_value_get(self, key, /, default=None):
        raise NotImplementedError


##


@dc.dataclass()
class DuplicateUniqueTypedValueError(Exception, ta.Generic[UniqueTypedValueU]):
    cls: type[UniqueTypedValueU]
    new: UniqueTypedValueU
    old: UniqueTypedValueU


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
        if not isinstance(key, type):
            if default is not None:
                raise RuntimeError('Must not provide both an instance key and a default')
            default = key
            key = type(default)
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


##


class TypedValueGeneric(lang.Abstract, ta.Generic[TypedValueT]):
    _typed_value_type: ta.ClassVar[rfl.Type]

    def __init_subclass__(cls, **kwargs: ta.Any) -> None:
        super().__init_subclass__(**kwargs)

        if '_typed_value_type' in cls.__dict__:
            return

        g_mro = rfl.ALIAS_UPDATING_GENERIC_SUBSTITUTION.generic_mro(cls)
        g_tvg = check.single(
            gb
            for gb in g_mro
            if isinstance(gb, rfl.Generic) and gb.cls is TypedValueGeneric
        )
        tvt = check.single(g_tvg.args)
        cls._typed_value_type = tvt


##


class TypedValueContainer(
    TypedValuesAccessor[TypedValueT],
    TypedValueGeneric[TypedValueT],
    lang.Abstract,
):
    @property
    @abc.abstractmethod
    def _typed_values(self) -> TypedValues[TypedValueT] | None:
        raise NotImplementedError

    #

    def _typed_value_contains(self, cls):
        if (tvs := self._typed_values) is not None:
            return cls in tvs
        return False

    def _typed_value_getitem(self, key):
        if (tvs := self._typed_values) is not None:
            return tvs[key]
        if isinstance(key, int):
            raise IndexError(key)
        elif isinstance(key, type):
            raise KeyError(key)
        else:
            raise TypeError(key)

    def _typed_value_get(self, key, /, default=None):
        if (tvs := self._typed_values) is not None:
            return tvs.get(key, default)
        if not isinstance(key, type):
            if default is not None:
                raise RuntimeError('Must not provide both an instance key and a default')
            default = key
            key = type(default)
        check.issubclass(key, TypedValue)
        if issubclass(key, UniqueTypedValue):
            return default
        elif default is not None:
            return list(default)
        else:
            return []
