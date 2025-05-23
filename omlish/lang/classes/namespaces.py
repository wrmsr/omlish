import abc
import typing as ta

from .restrict import NotInstantiable


V = ta.TypeVar('V')


##


class GenericNamespaceMeta(abc.ABCMeta, ta.Generic[V]):
    __namespace_value_type__: ta.ClassVar[type | tuple[type, ...] | None] = None

    __namespace_values__: dict[str, V]

    def __new__(mcls, name, bases, namespace):
        if bases:
            for nc in (NotInstantiable,):
                if nc not in bases:
                    bases += (nc,)

        cls = super().__new__(mcls, name, bases, namespace)

        vt = cls.__namespace_value_type__

        dct: dict[str, V] = {}
        for b_cls in reversed(cls.__mro__):
            # FIXME: must list() to avoid `RuntimeError: dictionary changed size during iteration`
            for att in list(b_cls.__dict__):
                if att.startswith('_') or att in dct:
                    continue

                obj = getattr(cls, att)
                if vt is not None and not isinstance(obj, vt):
                    raise TypeError(obj)

                dct[att] = obj

        cls.__namespace_values__ = dct

        return cls

    def __iter__(cls) -> ta.Iterator[tuple[str, V]]:
        return iter(cls.__namespace_values__.items())

    def __getitem__(cls, n: str) -> V:
        return cls.__namespace_values__[n]


class NamespaceMeta(GenericNamespaceMeta[ta.Any]):
    pass


class Namespace(metaclass=NamespaceMeta):
    pass
