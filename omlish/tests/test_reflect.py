import typing as ta


Reflected = ta.Union[
    type,
    'Generic',
    'Union',
]


class Generic(ta.NamedTuple):
    cls: ta.Any
    args: ta.Sequence[Reflected]


class Union(ta.NamedTuple):
    lst: ta.Sequence[Reflected]


def reflect_type(obj: ta.Any) -> Reflected:
    if isinstance(obj, type):
        return obj
    raise NotImplementedError


def test_reflect_type():
    print(reflect_type(int))
