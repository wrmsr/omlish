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
        """The beginning of a sentence."""

    class Eos(StandardSpecialToken):
        """The end of a sentence."""

    class Unk(StandardSpecialToken):
        """An out-of-vocabulary token."""

    class Sep(StandardSpecialToken):
        """Separates two different sentences in the same input (used by BERT for instance)."""

    class Pad(StandardSpecialToken):
        """
        Used to make arrays of tokens the same size for batching purpose. Will then be ignored by attention mechanisms
        or loss computation.
        """

    class Cls(StandardSpecialToken):
        """The class of the input (used by BERT for instance)."""

    class Mask(StandardSpecialToken):
        """A masked token (used by masked-language modeling pretraining objectives, like BERT)."""


##


class AmbiguousSpecialTokenError(Exception):
    pass


class SpecialTokens:
    def __init__(self, stks: ta.Iterable[SpecialToken]) -> None:
        super().__init__()

        all_: list[SpecialToken] = []
        by_type: dict[type[SpecialToken], list[SpecialToken]] = {}
        by_int: dict[int, list[SpecialToken]] = {}
        for stk in stks:
            check.isinstance(stk, SpecialToken)
            all_.append(stk)
            by_type.setdefault(type(stk), []).append(stk)
            by_int.setdefault(int(stk), []).append(stk)

        self._all = all_
        self._by_type = by_type
        self._by_int = by_int

    @classmethod
    def from_dict(cls, dct: ta.Mapping[type[SpecialToken], int | None]) -> 'SpecialTokens':
        lst: list[SpecialToken] = []
        for ty, i in dct.items():
            if i is None:
                continue
            check.is_(type(i), int)
            lst.append(check.issubclass(ty, SpecialToken)(i))
        return cls(lst)

    @property
    def all(self) -> ta.Sequence[SpecialToken]:
        return self._all

    @property
    def by_type(self) -> ta.Mapping[type[SpecialToken], ta.Sequence[SpecialToken]]:
        return self._by_type

    @property
    def by_int(self) -> ta.Mapping[int, ta.Sequence[SpecialToken]]:
        return self._by_int

    #

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({sorted(self._all)!r})'

    #

    def __len__(self) -> int:
        return len(self._all)

    def __iter__(self) -> ta.Iterator[SpecialToken]:
        return iter(self._all)

    def __contains__(self, item: SpecialToken | type[SpecialToken]) -> bool:
        if isinstance(item, SpecialToken):
            return item in self._by_int
        elif isinstance(item, type):
            check.issubclass(item, SpecialToken)
            return item in self._by_type
        else:
            raise TypeError(item)

    def _check_single(self, ret: SpecialTokenT, *rest: SpecialTokenT) -> SpecialTokenT:
        if rest:
            raise AmbiguousSpecialTokenError([ret, *rest])
        return ret

    def __getitem__(self, item: SpecialTokenT | type[SpecialTokenT]) -> SpecialTokenT:
        if isinstance(item, SpecialToken):
            if item not in self._by_int:
                raise KeyError(item)
            return self._check_single(*item)  # type: ignore[misc]
        elif isinstance(item, type):
            return self._check_single(*self._by_type[check.issubclass(item, SpecialToken)])  # type: ignore[return-value]  # noqa
        else:
            raise TypeError(item)

    @ta.overload
    def get(
            self,
            item: SpecialTokenT | type[SpecialTokenT],
            default: SpecialTokenT,
    ) -> SpecialTokenT:
        ...

    @ta.overload
    def get(
            self,
            item: SpecialTokenT | type[SpecialTokenT],
            default: ta.Optional[SpecialTokenT] = None,  # noqa
    ) -> ta.Optional[SpecialTokenT]:  # noqa
        ...

    def get(self, item, default=None):
        try:
            return self[item]
        except KeyError:
            return default

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
        any_dct[cls] = ret  # type: ignore[assignment]
        return ret
