import ast
import types
import typing as ta


T = ta.TypeVar('T')


##


def repr_round_trip_value(v: T) -> T:
    r = repr(v)
    v2 = ast.literal_eval(r)
    if v != v2:
        raise ValueError(v)
    return v2


def set_qualname(cls: type, value: T) -> T:
    if isinstance(value, types.FunctionType):
        value.__qualname__ = f'{cls.__qualname__}.{value.__name__}'
    return value


def set_new_attribute(cls: type, name: str, value: ta.Any) -> bool:
    if name in cls.__dict__:
        return True
    set_qualname(cls, value)
    setattr(cls, name, value)
    return False

