import typing as ta


NoneType = type(None)


_GenericAlias = ta._GenericAlias  # type: ignore  # noqa
_UnionGenericAlias = ta._UnionGenericAlias  # type: ignore  # noqa


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

    @property
    def is_optional(self) -> bool:
        return NoneType in self.lst


def reflect(obj: ta.Any) -> Reflected:
    if isinstance(obj, type):
        return obj
    if type(obj) is _UnionGenericAlias:
        return Union([reflect(a) for a in obj.__args__])
    if type(obj) is _GenericAlias:
        return Generic(reflect(obj.__origin__), [reflect(a) for a in obj.__args__])
    raise NotImplementedError
