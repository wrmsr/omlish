"""
TODO:
 - generic omlish.dispatch - tuple[T, U], best-match, reject ambiguous
 - every method is a dispatch.method, call unbound - Doubler.double(5)
 - cache instances, invalidate on register
"""
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
            return

        for base in rfl.get_orig_bases(cls):
            rty = rfl.type_(base)
            if not (isinstance(rty, rfl.Generic) and Typeclass in rty.cls.__bases__):
                continue

            dct = _TYPECLASS_IMPLS[rty.cls]  # noqa
            arg = check.single(rty.args)
            if arg in dct:
                raise KeyError(arg)
            dct[arg] = cls

    def __new__(cls, *args, **kwargs):
        if Typeclass not in cls.__bases__:
            return super().__new__(cls, *args, **kwargs)

        raise NotImplementedError

    class _GenericAliasHandler:
        def __init__(self, alias):
            self._alias = alias

        def __call__(self, *args, **kwargs):
            ret = self._alias.__class__.__call__(self._alias, *args, **kwargs)

            return ret

    @classmethod
    def __class_getitem__(cls, item):
        ret = super().__class_getitem__(item)  # noqa

        if not isinstance(ret.__call__, Typeclass._GenericAliasHandler):
            ret.__call__ = Typeclass._GenericAliasHandler(ret)

        return ret


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
