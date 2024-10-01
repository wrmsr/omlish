"""
TODO:
 - generic omlish.dispatch - tuple[T, U], best-match, reject ambiguous
 - every method is a dispatch.method, call unbound - Doubler.double(5)
  - what's 'self'? are they are made classmethods?
  - doesn't dispatch on first arg, dispatches on T (if present)
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
import functools
import inspect
import typing as ta

from omlish import check
from omlish import lang
from omlish import reflect as rfl


T = ta.TypeVar('T')
TypeclassT = ta.TypeVar('TypeclassT', bound='Typeclass')


_IS_TYPECLASS_METHOD_ATTR = '__istypeclassmethod__'


def typeclassmethod(funcobj):
    setattr(funcobj, _IS_TYPECLASS_METHOD_ATTR, True)
    return abc.abstractmethod(funcobj)


class Typeclass(abc.ABC, ta.Generic[T]):
    @dc.dataclass(frozen=True)
    class _Impl:
        cls: type['Typeclass']
        arg: rfl.Type

        _: dc.KW_ONLY

        singleton: bool | None

    @dc.dataclass(frozen=True)
    class _Internals:
        cls: type['Typeclass']

        _: dc.KW_ONLY

        singleton: bool | None
        tcms: ta.Mapping[str, ta.Any]

        impls: dict[rfl.Type, 'Typeclass._Impl'] = dc.field(default_factory=dict)
        insts: dict[rfl.Type, 'Typeclass'] = dc.field(default_factory=dict)

        def dispatch(
                self,
                tca: rfl.Type,
                *args: ta.Any,
                **kwargs: ta.Any,
        ) -> 'Typeclass':
            try:
                return self.insts[tca]
            except KeyError:
                pass

            impl = self.impls[tca]

            result = impl.cls(*args, **kwargs)
            result.__orig_class__ = self.cls[tca]  # type: ignore

            if self.singleton or impl.singleton:
                self.insts[tca] = result

            return result

    __typeclass_internals__: ta.ClassVar[_Internals]

    #

    def __init_subclass__(
            cls,
            *,
            singleton: bool | None = None,
            **kwargs: ta.Any,
    ) -> None:
        super().__init_subclass__(**kwargs)

        if Typeclass in cls.__bases__:
            rty = rfl.type_(cls)
            tca = check.single(rty.args)  # type: ignore
            tcv = check.isinstance(tca, ta.TypeVar)

            tcms: dict[str, ta.Any] = {}
            for a, v in list(cls.__dict__.items()):
                if not (
                    isinstance(v, classmethod) and
                    getattr(v.__func__, _IS_TYPECLASS_METHOD_ATTR, False)
                ):
                    continue

                sig = inspect.signature(v.__func__)
                params = list(sig.parameters.values())
                if len(params) < 2 or params[1].annotation is not tcv:
                    continue

                tcm = functools.partial(cls.__typeclass_classmethod__, a, v)
                functools.update_wrapper(tcm, v.__func__)
                setattr(cls, a, tcm)
                tcms[a] = tcm

            cls.__typeclass_internals__ = Typeclass._Internals(
                cls,
                singleton=singleton,
                tcms=tcms,
            )

        else:
            cls.__typeclass_internals__ = lang.access_forbidden()

            for base in rfl.get_orig_bases(cls):
                rty = rfl.type_(base)
                if not (isinstance(rty, rfl.Generic) and Typeclass in rty.cls.__bases__):
                    continue

                intr: Typeclass._Internals = rty.cls.__typeclass_internals__  # type: ignore
                tca = check.single(rty.args)

                if tca in intr.impls:
                    raise KeyError(tca)

                intr.impls[tca] = Typeclass._Impl(
                    cls,
                    tca,
                    singleton=singleton,
                )

    #

    def __new__(cls, *args, **kwargs):
        if Typeclass not in cls.__bases__:
            return super().__new__(cls, *args, **kwargs)

        raise TypeError(cls)

    #

    @classmethod
    def dispatch(
            cls: type[TypeclassT],
            tca: ta.Any,
            *args: ta.Any,
            **kwargs: ta.Any,
    ) -> TypeclassT:
        if Typeclass not in cls.__bases__:
            raise TypeError(cls)

        intr: Typeclass._Internals = cls.__typeclass_internals__  # noqa
        inst = intr.dispatch(tca, *args, **kwargs)
        return inst  # type: ignore

    #

    @classmethod
    def __typeclass_classmethod__(
            cls,
            attr: str,
            cm: classmethod,
            *args: ta.Any,
            **kwargs: ta.Any,
    ) -> ta.Any:
        if Typeclass not in cls.__bases__:
            raise TypeError(cls)

        tca = args[0].__class__
        inst = cls.dispatch(tca)
        fn = getattr(inst, attr)
        return fn(*args, **kwargs)

    #

    class _DispatchingGenericAlias(ta._GenericAlias, _root=True):  # type: ignore  # noqa
        def __call__(self, *args, **kwargs):
            intr: Typeclass._Internals = self.__origin__.__typeclass_internals__  # noqa
            tca = check.single(self.__args__)
            return intr.dispatch(tca, *args, **kwargs)

    rfl.types._SIMPLE_GENERIC_ALIAS_TYPES.add(_DispatchingGenericAlias)  # noqa

    @classmethod
    def __class_getitem__(cls, item):
        ret = super().__class_getitem__(item)  # type: ignore

        if Typeclass in cls.__bases__ and not isinstance(ret, Typeclass._DispatchingGenericAlias):
            ret.__class__ = Typeclass._DispatchingGenericAlias

        return ret


##


class Doubler(Typeclass[T], singleton=True):
    @classmethod
    @typeclassmethod
    def double(cls, x: T) -> T:
        raise NotImplementedError


class _IntDoubler(Doubler[int]):
    @classmethod
    def double(cls, x: int) -> int:
        return x * 2


class _StrDoubler(Doubler[str]):
    @classmethod
    def double(cls, x: str) -> str:
        return x * 2


class _ListDoubler(Doubler[list]):
    def double(self, x: list) -> list:
        # return [Doubler[type(e)]().double(e) for e in x]
        return [Doubler.double(e) for e in x]


def _main() -> None:
    assert (di0 := Doubler[int]()).double(21) == 42
    assert (di1 := Doubler[int]()).double(21) == 42
    assert di0 is di1

    assert Doubler[list]().double([5, 'a', [10, 'b']]) == [10, 'aa', [20, 'bb']]

    assert Doubler.double(5) == 10


if __name__ == '__main__':
    _main()
