import ast
import typing as ta


T = ta.TypeVar('T')


##


def repr_round_trip_value(v: T) -> T:
    r = repr(v)
    v2 = ast.literal_eval(r)
    if v != v2:
        raise ValueError(v)
    return v2
