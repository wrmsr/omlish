"""
TODO:
 - generic omlish.dispatch - tuple[T, U], best-match, reject ambiguous
 - every method is a dispatch.method, call unbound - Doubler.double(5)
  - !! doesn't dispatch on first arg, dispatches on T (if present)
 - cache instances, invalidate on register
"""
import abc
import typing as ta

from omlish import check
from omlish import lang
from omlish import reflect as rfl


T = ta.TypeVar('T')
TypeclassT = ta.TypeVar('TypeclassT', bound='Typeclass')


class Typeclass(abc.ABC, ta.Generic[T]):
    _impls: ta.ClassVar[dict[rfl.Type, type['Typeclass']]]

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        if Typeclass in cls.__bases__:
            # TODO: assert Double.double(5) == 10 -- dispatch.method
            # for a, v in cls.__dict__.items():
            #     if getattr(v, '__isabstractmethod__', False):
            #         continue
            #
            #     raise NotImplementedError

            cls._impls = {}

        else:
            cls._impls = lang.access_forbidden('_impls')

            for base in rfl.get_orig_bases(cls):
                rty = rfl.type_(base)
                if not (isinstance(rty, rfl.Generic) and Typeclass in rty.cls.__bases__):
                    continue

                impls = rty.cls._impls  # noqa
                arg = check.single(rty.args)
                if arg in impls:
                    raise KeyError(arg)
                impls[arg] = cls

    def __new__(cls, *args, **kwargs):
        if Typeclass not in cls.__bases__:
            return super().__new__(cls, *args, **kwargs)

        raise NotImplementedError

    class _DispatchingGenericAlias(ta._GenericAlias, _root=True):  # noqa
        def __call__(self, *args, **kwargs):
            impl = lookup_typeclass(self.__origin__, check.single(self.__args__))

            result = impl(*args, **kwargs)
            result.__orig_class__ = self
            return result

    rfl.types._SIMPLE_GENERIC_ALIAS_TYPES.add(_DispatchingGenericAlias)  # noqa

    @classmethod
    def __class_getitem__(cls, item):
        ret = super().__class_getitem__(item)  # noqa

        if Typeclass in cls.__bases__ and not isinstance(ret, Typeclass._DispatchingGenericAlias):
            ret.__class__ = Typeclass._DispatchingGenericAlias

        return ret


def lookup_typeclass(cls: type[TypeclassT], arg: rfl.Type) -> type[TypeclassT]:
    return cls._impls[arg]

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
    # assert Doubler.double(21) == 42


if __name__ == '__main__':
    _main()
