import abc
import dataclasses as dc
import typing as ta

from omlish import check
from omlish import lang

from .idents import IDENT_PREFIX


T = ta.TypeVar('T')


##


@dc.dataclass(frozen=True)
class OpRef(ta.Generic[T]):
    name: str

    def __post_init__(self) -> None:
        check.non_empty_str(self.name)

    def ident(self) -> str:
        return IDENT_PREFIX + lang.replace_many(self.name, '.[]', '__')


OpRefMap: ta.TypeAlias = ta.Mapping[OpRef, ta.Any]


##


@dc.dataclass(frozen=True)
class Op(abc.ABC):  # noqa
    pass


@dc.dataclass(frozen=True)
class SetAttrOp(Op):
    name: str
    value: ta.Any
    if_present: ta.Literal['skip', 'replace', 'raise']


@dc.dataclass(frozen=True)
class AddMethodOp(Op):
    name: str
    src: str
    refs: frozenset[OpRef] = frozenset()
