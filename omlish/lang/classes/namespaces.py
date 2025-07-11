import abc
import typing as ta

from .abstract import Abstract
from .restrict import NotInstantiable


V = ta.TypeVar('V')


##


class _NOT_SET:  # noqa
    def __new__(cls, *args, **kwargs):  # noqa
        raise TypeError


NamespaceCheckValue: ta.TypeAlias = type | tuple[type, ...] | ta.Callable[[ta.Any], bool]


class GenericNamespaceMeta(abc.ABCMeta, ta.Generic[V]):
    __namespace_check_values__: NamespaceCheckValue | None = None
    __namespace_case_insensitive__: bool = False

    def __init_subclass__(
            mcls,
            *,
            check_values: NamespaceCheckValue | None | type[_NOT_SET] = _NOT_SET,
            case_insensitive: bool | type[_NOT_SET] = _NOT_SET,
            **kwargs,
    ):
        super().__init_subclass__(**kwargs)

        if check_values is not _NOT_SET:
            mcls.__namespace_check_values__ = check_values
        if case_insensitive is not _NOT_SET:
            mcls.__namespace_case_insensitive__ = case_insensitive  # type: ignore

    __namespace_attrs__: ta.Mapping[str, V]
    __namespace_values__: ta.Mapping[str, V]

    def __new__(
            mcls,
            name,
            bases,
            namespace,
            *,
            check_values: NamespaceCheckValue | None | type[_NOT_SET] = _NOT_SET,
            case_insensitive: bool | type[_NOT_SET] = _NOT_SET,
            **kwargs,
    ):
        if bases:
            if NotInstantiable not in bases and not any(NotInstantiable in b.__mro__ for b in bases):
                if Abstract in bases:
                    # Must go before Abstract for mro because NotInstantiable is itself Abstract
                    ai = bases.index(Abstract)
                    bases = (*bases[:ai], NotInstantiable, *bases[ai:])
                else:
                    bases += (NotInstantiable,)

        if check_values is _NOT_SET:
            check_values = mcls.__namespace_check_values__
        if case_insensitive is _NOT_SET:
            case_insensitive = mcls.__namespace_case_insensitive__

        cls = super().__new__(
            mcls,
            name,
            bases,
            namespace,
            **kwargs,
        )

        cls.__namespace_check_values__ = check_values
        cls.__namespace_case_insensitive__ = case_insensitive  # type: ignore

        if isinstance(check_values, (type, tuple)):
            cvt = check_values

            def _cv(o):
                if not isinstance(o, cvt):
                    raise TypeError(o, cvt)
                return True

            check_values = _cv

        a_dct: dict[str, V] = {}
        v_dct: dict[str, V] = {}
        for b_cls in cls.__mro__[-2::-1]:
            # FIXME: must list() to avoid `RuntimeError: dictionary changed size during iteration`
            for att in list(b_cls.__dict__):
                if att.startswith('_') or att in a_dct:
                    continue

                name = att
                if case_insensitive:
                    name = att.lower()
                    if name in v_dct:
                        raise NameError(f'Ambiguous case-insensitive namespace attr: {name!r}, {att!r}')

                obj = getattr(cls, att)
                if check_values is not None and not check_values(obj):
                    raise ValueError(obj)

                a_dct[att] = obj
                v_dct[name] = obj

        cls.__namespace_attrs__ = a_dct
        cls.__namespace_values__ = v_dct

        return cls

    def __iter__(cls) -> ta.Iterator[tuple[str, V]]:
        return iter(cls.__namespace_attrs__.items())

    def __contains__(self, n: str) -> bool:
        return n in self.__namespace_values__

    def __getitem__(cls, n: str) -> V:
        if cls.__namespace_case_insensitive__:
            n = n.lower()
        return cls.__namespace_values__[n]


class NamespaceMeta(GenericNamespaceMeta[ta.Any]):
    pass


class Namespace(metaclass=NamespaceMeta):
    pass
