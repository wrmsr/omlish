import typing as ta

from ..objects import super_meta
from ..strings import is_dunder


##


class _IntersectionMeta(type):
    __intersection_bases__: ta.ClassVar[tuple[type, ...]]

    def __new__(cls, name, bases, dct):
        if ks := sorted(k for k in dct if not is_dunder(k)):
            raise TypeError(f'Intersection classes cannot have contents: {ks!r}')

        try:
            ibc = Intersection
        except NameError:
            # Bootstrapping Intersection itself - it gets an empty bases tuple purely for attribute uniformity, the
            # check hooks below special-case it before consulting this.
            dct.update(__intersection_bases__=())
            return super_meta(super(), cls, name, bases, dct)

        ibl: list[type] = []
        ibs: set[type] = set()
        for b in bases:
            if b is ibc:
                continue
            elif isinstance(b, _IntersectionMeta):
                for ib in b.__intersection_bases__:
                    if ib not in ibs:
                        ibl.append(ib)
                        ibs.add(ib)
            else:
                if b not in ibs:
                    ibl.append(b)
                    ibs.add(b)
        dct.update(__intersection_bases__=tuple(ibl))

        return super_meta(super(), cls, name, bases, dct)

    def __instancecheck__(cls, instance: object) -> bool:
        if cls is Intersection:
            raise TypeError('isinstance cannot be checked against Intersection itself')
        return all(isinstance(instance, ib) for ib in cls.__intersection_bases__)

    def __subclasscheck__(cls, subclass: type) -> bool:
        # Against Intersection itself the check is nominal - 'is subclass an intersection class' - as with
        # issubclass(X, ta.Protocol). Concrete intersection classes really do inherit Intersection, so the default
        # type check answers this exactly.
        if cls is Intersection:
            return super().__subclasscheck__(subclass)
        return all(issubclass(subclass, ib) for ib in cls.__intersection_bases__)


class Intersection(metaclass=_IntersectionMeta):
    __slots__ = ()

    @ta.final
    def __new__(cls, *args, **kwargs):  # noqa
        raise TypeError

    @ta.final
    def __init__(self) -> None:
        raise TypeError
