"""
TODO:
 - final check
"""
import abc
import typing as ta


class NotInstantiable(abc.ABC):
    __slots__ = ()

    def __new__(cls, *args, **kwargs) -> ta.NoReturn:  # type: ignore
        raise TypeError


class Final(abc.ABC):
    pass


class _Namespace(Final):

    def __mro_entries__(self, bases, **kwargs):
        return (Final, NotInstantiable)


Namespace: type = _Namespace()  # type: ignore
