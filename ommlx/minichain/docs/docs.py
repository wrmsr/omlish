import typing as ta

from omlish import cached
from omlish import collections as col
from omlish import dataclasses as dc
from omlish import lang

from .dtypes import Dtype


##


@dc.dataclass(frozen=True)
class FieldRef(lang.Final):
    n: str = dc.xfield(check_type=True)

    def __str__(self) -> str:
        return f':{self.n}'


def f(o: str | FieldRef) -> FieldRef:
    if isinstance(o, FieldRef):
        return o
    return FieldRef(o)


def f_(o: str | FieldRef) -> str:
    if isinstance(o, str):
        return o
    elif isinstance(o, FieldRef):
        return o.n
    else:
        raise TypeError(o)


##


@dc.dataclass(frozen=True)
class DocField(lang.Final):
    name: str
    dtype: Dtype


@dc.dataclass(frozen=True)
class DocSchema(lang.Final):
    fields: ta.Sequence[DocField] = dc.xfield(validate=lambda v: all(isinstance(e, DocField) for e in v))

    @cached.property
    @dc.init
    def fields_by_name(self) -> ta.Mapping[str, DocField]:
        return col.make_map_by(lambda f: f.name, self.fields, strict=True)  # noqa

    def __getitem__(self, key: str | FieldRef) -> DocField:
        return self.fields_by_name[f_(key)]


@dc.dataclass(frozen=True)
class Doc(lang.Final):
    values: ta.Mapping[str, ta.Any]

    def __getitem__(self, key: str | FieldRef) -> DocField:
        return self.values[f_(key)]
