"""
TODO:
 - statics? once, every, and_every, ...
 - io - FileObj protocol
 - cached_unary?
 - s/cached/memoized/?
 - @classmethod with instancemethod override/overload
 - functools.partial but check prototype fits (kwargs, #args)
 - curry
  - functions.py..
 - no_bool class/staticmethod
"""
import time
import typing as ta


T = ta.TypeVar('T')
K = ta.TypeVar('K')
V = ta.TypeVar('V')

BytesLike = ta.Union[bytes, bytearray]


def register_on(reg, name=None):
    def inner(obj):
        obj_name = name if name is not None else obj.__name__
        if hasattr(reg, obj_name):
            raise NameError(obj_name)
        setattr(reg, obj_name, obj)
        return obj
    return inner


class VoidException(Exception):
    pass


class Void:

    def __new__(cls, *args, **kwargs):
        raise VoidException

    def __init_subclass__(cls, **kwargs):
        raise VoidException


def void(*args, **kwargs) -> ta.NoReturn:
    raise VoidException


def make_cell(value: ta.Any) -> 'CellType':  # type: ignore
    def fn():
        nonlocal value
    return fn.__closure__[0]  # type: ignore


CellType = type(make_cell(None))


class EmptyMap(ta.Mapping[K, V]):

    INSTANCE: ta.Optional['EmptyMap[K, V]'] = None

    def __init_subclass__(cls, **kwargs):
        raise TypeError

    def __new__(cls, *args, **kwargs):
        if args or kwargs:
            raise TypeError
        return EmptyMap.INSTANCE

    def __repr__(self) -> str:
        return 'EmptyMap()'

    def __init__(self) -> None:
        super().__init__()

    def __getitem__(self, k: K) -> V:
        raise KeyError

    def __len__(self) -> int:
        return 0

    def __iter__(self) -> ta.Iterator[K]:
        return
        yield  # type: ignore


EmptyMap.INSTANCE = object.__new__(EmptyMap)  # type: ignore


def empty_map():
    return EmptyMap.INSTANCE


def is_not_none(obj: T) -> bool:
    return obj is not None


class TimeoutException(Exception):
    pass


def ticking_timeout(s: ta.Union[int, float, None]) -> ta.Callable[[], None]:
    if s is None:
        return lambda: None
    def tick():  # noqa
        if time.time() >= deadline:
            raise TimeoutException
    deadline = time.time() + s
    return tick
