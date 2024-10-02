import typing as ta

from omlish import lang


OptionT = ta.TypeVar('OptionT', bound='Option')
OptionU = ta.TypeVar('OptionU', bound='Option')
UniqueOptionU = ta.TypeVar('UniqueOptionU', bound='UniqueOption')


##


class Option(lang.Abstract):
    pass


class UniqueOption(Option):
    unique_option_cls: ta.ClassVar[type[Option]]

    def __init_subclass__(cls, **kwargs: ta.Any) -> None:
        super().__init_subclass__(**kwargs)

        if UniqueOption in cls.__bases__:
            cls.unique_option_cls = cls


##


class Options(lang.Final, ta.Generic[OptionT]):
    def __init__(self, *options: OptionT, override: bool = False) -> None:
        super().__init__()

        self._lst = options

        dct: dict = {}
        for o in options:
            if isinstance(o, UniqueOption):
                if not override and type(o) in dct:
                    raise KeyError(type(o))
                dct[type(o)] = o
            else:
                dct.setdefault(type(o), []).append(o)
        self._dct = dct

    def __iter__(self) -> ta.Iterator[OptionT]:
        return iter(self._lst)

    def __len__(self) -> int:
        return len(self._lst)

    @ta.overload
    def __getitem__(self, cls: type[UniqueOptionU]) -> UniqueOptionU:  # type: ignore[overload-overlap]
        ...

    @ta.overload
    def __getitem__(self, cls: type[OptionU]) -> ta.Sequence[OptionU]:
        ...

    def __getitem__(self, cls):
        return self._dct[cls]
