import abc
import typing as ta

from omlish import check
from omlish import reflect as rfl


T = ta.TypeVar('T')
TypeclassT = ta.TypeVar('TypeclassT', bound='Typeclass')


_TYPECLASS_IMPLS: dict[type['Typeclass'], dict[rfl.Type, type['Typeclass']]] = {}


class Typeclass(abc.ABC, ta.Generic[T]):
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if Typeclass in cls.__bases__:
            _TYPECLASS_IMPLS[cls] = {}
        else:
            for base in rfl.get_orig_bases(cls):
                rty = rfl.type_(base)
                if isinstance(rty, rfl.Generic) and Typeclass in rty.cls.__bases__:
                    dct = _TYPECLASS_IMPLS[rty.cls]  # noqa
                    arg = check.single(rty.args)
                    if arg in dct:
                        raise KeyError(arg)
                    dct[arg] = cls

    def __new__(cls, *args, **kwargs):
        if Typeclass not in cls.__bases__:
            return super().__new__(cls, *args, **kwargs)

        raise NotImplementedError


def lookup_typeclass(cls: type[TypeclassT], arg: rfl.Type) -> type[TypeclassT]:
    return _TYPECLASS_IMPLS[cls][arg]


class Doubler(Typeclass[T]):
    @abc.abstractmethod
    def double(self, x: T) -> T:
        raise NotImplementedError


class _(Doubler[int]):
    def double(self, x: int) -> int:
        return x * 2


def _main() -> None:
    assert lookup_typeclass(Doubler, int)().double(21) == 42
    assert Doubler[int]().double(21) == 42


if __name__ == '__main__':
    _main()
