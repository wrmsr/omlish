import typing as ta

from omlish import lang


class A:
    def a(self):
        pass


class B:
    def b(self):
        pass


class C:
    def c(self):
        pass


##


class _IntersectionMeta(type):
    __intersection_bases__: ta.ClassVar[tuple[type, ...]]

    def __new__(cls, name, bases, dct):
        if ks := sorted(k for k in dct if not lang.is_dunder(k)):
            raise TypeError(f'Intersection classes cannot have contents: {ks!r}')

        try:
            ibc = Intersection
        except NameError:
            return lang.super_meta(super(), cls, name, bases, dct)

        ibl: list[type] = []
        ibs: set[type] = set()
        for b in bases:
            if b is ibc:
                continue
            elif isinstance(type(b), _IntersectionMeta):
                for ib in b.__intersection_bases__:
                    if ib not in ibs:
                        ibl.append(ib)
                        ibs.add(ib)
            else:
                if b not in ibs:
                    ibl.append(b)
                    ibs.add(b)
        dct.update(__intersection_bases__=tuple(ibl))

        return lang.super_meta(super(), cls, name, bases, dct)

    def __instancecheck__(cls, instance: object) -> bool:
        return all(isinstance(instance, ib) for ib in cls.__intersection_bases__)

    def __subclasscheck__(cls, subclass: type) -> bool:
        return all(issubclass(subclass, ib) for ib in cls.__intersection_bases__)


class Intersection(metaclass=_IntersectionMeta):
    __slots__ = ()

    @ta.final
    def __new__(cls, *args, **kwargs):  # noqa
        raise TypeError

    @ta.final
    def __init__(self) -> None:
        raise TypeError


##


class ABIntersection(A, B, Intersection):
    pass


def _main() -> None:
    class _AB(A, B):
        pass

    assert isinstance(_AB(), ABIntersection)
    assert issubclass(_AB, ABIntersection)

    class _BA(B, A):
        pass

    assert isinstance(_BA(), ABIntersection)
    assert issubclass(_BA, ABIntersection)

    class _ABC(A, B, C):
        pass

    assert isinstance(_ABC(), ABIntersection)
    assert issubclass(_ABC, ABIntersection)

    class _AC(A, C):
        pass

    assert not isinstance(_AC(), ABIntersection)
    assert not issubclass(_AC, ABIntersection)


if __name__ == '__main__':
    _main()
