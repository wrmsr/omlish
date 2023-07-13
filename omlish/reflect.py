import collections.abc
import typing as ta


NoneType = type(None)


_GenericAlias = ta._GenericAlias  # type: ignore  # noqa
_UnionGenericAlias = ta._UnionGenericAlias  # type: ignore  # noqa


Reflected = ta.Union[
    type,
    'Union',
    'Generic',
]


class Union(ta.NamedTuple):
    args: ta.Sequence[Reflected]

    @property
    def is_optional(self) -> bool:
        return NoneType in self.args


class Generic(ta.NamedTuple):
    cls: ta.Any
    args: ta.Sequence[Reflected]


REFLECTED_TYPES = (
    type,
    Union,
    Generic,
)


def reflect(obj: ta.Any) -> Reflected:
    if isinstance(obj, (Union, Generic)):
        return obj

    if type(obj) is _UnionGenericAlias:
        return Union(tuple(reflect(a) for a in ta.get_args(obj)))

    if type(obj) is _GenericAlias or type(obj) is ta.GenericAlias:  # type: ignore  # noqa
        return Generic(reflect(ta.get_origin(obj)), tuple(reflect(a) for a in ta.get_args(obj)))

    if isinstance(obj, type):
        return obj

    raise TypeError(obj)


##


KNOWN_GENERICS: ta.AbstractSet[type] = frozenset([
    collections.abc.Mapping,
    collections.abc.Sequence,
    collections.abc.Set,
])


def isinstance_of(rfl: Reflected) -> ta.Callable[[ta.Any], bool]:
    if isinstance(rfl, type):
        return lambda o: isinstance(o, rfl)  # type: ignore

    if isinstance(rfl, Union):
        fns = [isinstance_of(a) for a in rfl.args]
        return lambda o: any(fn(o) for fn in fns)

    if isinstance(rfl, Generic):
        if rfl.cls in (collections.abc.Sequence, collections.abc.Set):
            [efn] = map(isinstance_of, rfl.args)
            return lambda o: isinstance(o, rfl.cls) and all(efn(e) for e in o)  # type: ignore

        if rfl.cls == collections.abc.Mapping:
            kfn, vfn = map(isinstance_of, rfl.args)
            return lambda o: isinstance(o, rfl.cls) and all(kfn(k) and vfn(v) for k, v in o.items())  # type: ignore

    raise TypeError(rfl)
