import typing as ta

from omlish import check
from omlish import lang

from .types import SpecialToken


T = ta.TypeVar('T')
SpecialTokenT = ta.TypeVar('SpecialTokenT', bound=SpecialToken)


##


class SpecialTokenNamespaceMeta(
    lang.GenericNamespaceMeta[type[SpecialToken]],
    check_values=lang.issubclass_of(SpecialToken),
    case_insensitive=True,
):
    pass


class SpecialTokenNamespace(metaclass=SpecialTokenNamespaceMeta):
    pass


##


class StandardSpecialToken(
    SpecialToken,
    lang.Sealed,
    lang.Abstract,
):
    # Opting not to enforce for now.
    # def __new__(cls, *args, **kwargs):
    #     if lang.is_abstract_class(cls):
    #         raise lang.AbstractTypeError(cls)
    #     return super().__new__(cls, *args, **kwargs)

    pass


class StandardSpecialTokens(SpecialTokenNamespace, lang.Final):
    class Bos(StandardSpecialToken):
        pass

    class Eos(StandardSpecialToken):
        pass

    class Unk(StandardSpecialToken):
        pass

    class Sep(StandardSpecialToken):
        pass

    class Pad(StandardSpecialToken):
        pass

    class Cls(StandardSpecialToken):
        pass

    class Mask(StandardSpecialToken):
        pass


##


class SpecialTokens:
    def __init__(self, stks: ta.Iterable[SpecialToken]) -> None:
        super().__init__()

        all_: set[SpecialToken] = set()
        by_type: dict[type[SpecialToken], SpecialToken] = {}
        for stk in stks:
            check.isinstance(stk, SpecialToken)
            check.not_in(stk, all_)
            check.not_in(type(stk), by_type)
            all_.add(stk)
            by_type[type(stk)] = stk
        check.equal(len(all_), len(by_type))
        self._all = all_
        self._by_type = by_type

    @classmethod
    def from_dict(cls, dct: ta.Mapping[type[SpecialToken], int | None]) -> 'SpecialTokens':
        return cls([
            check.issubclass(ty, SpecialToken)(i)
            for ty, i in dct.items()
            if i is not None
        ])

    @property
    def by_type(self) -> ta.Mapping[type[SpecialToken], SpecialToken]:
        return self._by_type

    @property
    def all(self) -> ta.AbstractSet[SpecialToken]:
        return self._all

    #

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self._all!r})'

    #

    def __len__(self) -> int:
        return len(self._all)

    def __iter__(self) -> ta.Iterator[SpecialToken]:
        return iter(self._all)

    def __contains__(self, item: SpecialToken | type[SpecialToken]) -> bool:
        if isinstance(item, SpecialToken):
            return item in self._all
        elif isinstance(item, type):
            check.issubclass(item, SpecialToken)
            return item in self._by_type
        else:
            raise TypeError(item)

    def __getitem__(self, item: SpecialTokenT | type[SpecialTokenT]) -> SpecialTokenT:
        if isinstance(item, SpecialToken):
            if item not in self._all:
                raise KeyError(item)
            return ta.cast(SpecialTokenT, item)
        elif isinstance(item, type):
            return ta.cast(SpecialTokenT, self._by_type[check.issubclass(item, SpecialToken)])
        else:
            raise TypeError(item)

    #

    _any_dct: dict[type, tuple[SpecialToken, ...]]

    def get_any(self, cls: type[T]) -> ta.Sequence[T]:
        try:
            any_dct = self._any_dct
        except AttributeError:
            any_dct = {}
            self._any_dct = any_dct

        try:
            return any_dct[cls]  # type: ignore
        except KeyError:
            pass

        ret = tuple(tv for tv in self._all if isinstance(tv, cls))
        any_dct[cls] = ret
        return ret
