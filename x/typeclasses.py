"""
TODO:
 - generic omlish.dispatch - tuple[T, U], best-match, reject ambiguous
 - every method is a dispatch.method, call unbound - Doubler.double(5)
  - !! doesn't dispatch on first arg, dispatches on T (if present)
 - cache instances, invalidate on register

==

# TODO: assert Double.double(5) == 10 -- dispatch.method
# for a, v in cls.__dict__.items():
#     if getattr(v, '__isabstractmethod__', False):
#         continue
#
#     raise NotImplementedError

"""
import abc
import dataclasses as dc
import typing as ta

from omlish import check
from omlish import lang
from omlish import reflect as rfl


T = ta.TypeVar('T')
TypeclassT = ta.TypeVar('TypeclassT', bound='Typeclass')


class Typeclass(abc.ABC, ta.Generic[T]):
    @dc.dataclass(frozen=True)
    class _Impl:
        cls: type['Typeclass']
        arg: rfl.Type

        _: dc.KW_ONLY

        singleton: bool = False

    @dc.dataclass(frozen=True)
    class _Internals:
        cls: type['Typeclass']

        _: dc.KW_ONLY

        singleton: bool = False

        impls: dict[rfl.Type, 'Typeclass._Impl'] = dc.field(default_factory=dict)
        insts: dict[rfl.Type, 'Typeclass'] = dc.field(default_factory=dict)

    __typeclass_internals__: ta.ClassVar[_Internals]

    def __init_subclass__(
            cls,
            *,
            singleton: bool | None = None,
            **kwargs: ta.Any,
    ) -> None:
        super().__init_subclass__(**kwargs)

        if Typeclass in cls.__bases__:
            cls.__typeclass_internals__ = Typeclass._Internals(
                cls,
                singleton=singleton,
            )

        else:
            cls.__typeclass_internals__ = lang.access_forbidden()

            for base in rfl.get_orig_bases(cls):
                rty = rfl.type_(base)
                if not (isinstance(rty, rfl.Generic) and Typeclass in rty.cls.__bases__):
                    continue

                intr: Typeclass._Internals = rty.cls.__typeclass_internals__  # noqa
                arg = check.single(rty.args)

                if arg in intr.impls:
                    raise KeyError(arg)

                intr.impls[arg] = Typeclass._Impl(
                    cls,
                    arg,
                    singleton=singleton,
                )

    def __new__(cls, *args, **kwargs):
        if Typeclass not in cls.__bases__:
            return super().__new__(cls, *args, **kwargs)

        raise TypeError(cls)

    class _DispatchingGenericAlias(ta._GenericAlias, _root=True):  # noqa
        def __call__(self, *args, **kwargs):
            intr: Typeclass._Internals = self.__origin__.__typeclass_internals__  # noqa
            arg = check.single(self.__args__)

            if intr.insts is not None:
                try:
                    return intr.insts[arg]
                except KeyError:
                    pass

            impl = intr.impls[arg]

            result = impl.cls(*args, **kwargs)
            result.__orig_class__ = self

            if intr.singleton or impl.singleton:
                intr.insts[arg] = result

            return result

    rfl.types._SIMPLE_GENERIC_ALIAS_TYPES.add(_DispatchingGenericAlias)  # noqa

    @classmethod
    def __class_getitem__(cls, item):
        ret = super().__class_getitem__(item)  # noqa

        if Typeclass in cls.__bases__ and not isinstance(ret, Typeclass._DispatchingGenericAlias):
            ret.__class__ = Typeclass._DispatchingGenericAlias

        return ret


class Doubler(Typeclass[T], singleton=True):
    @abc.abstractmethod
    def double(self, x: T) -> T:
        raise NotImplementedError


class _(Doubler[int]):
    def double(self, x: int) -> int:
        return x * 2


def _main() -> None:
    assert Doubler[int]().double(21) == 42
    # assert Doubler.double(21) == 42


if __name__ == '__main__':
    _main()
