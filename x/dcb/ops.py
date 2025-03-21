import abc
import dataclasses as dc
import typing as ta

from omlish import check

from .idents import IDENT_PREFIX


T = ta.TypeVar('T')


##


@dc.dataclass(frozen=True)
class OpRef(ta.Generic[T]):
    name: str

    def __post_init__(self) -> None:
        check.non_empty_str(self.name)

    def ident(self) -> str:
        return IDENT_PREFIX + self.name.replace( '.', '__')


OpRefMap: ta.TypeAlias = ta.Mapping[OpRef, ta.Any]


##


@dc.dataclass(frozen=True)
class Op(abc.ABC):  # noqa
    pass


@dc.dataclass(frozen=True)
class SetAttrOp(Op):
    name: str
    value: OpRef | ta.Any
    if_present: ta.Literal['skip', 'replace', 'error']


@dc.dataclass(frozen=True)
class AddMethodOp(Op):
    name: str
    src: str
    refs: frozenset[OpRef] = frozenset()


@dc.dataclass(frozen=True)
class AddPropertyOp(Op):
    name: str
    get_src: str | None = None
    set_src: str | None = None
    del_src: str | None = None
    refs: frozenset[OpRef] = frozenset()


##


def get_op_refs(op: Op) -> frozenset[OpRef]:
    if isinstance(op, SetAttrOp):
        if isinstance(v := op.value, OpRef):
            return frozenset([v])
        else:
            return frozenset()

    elif isinstance(op, (AddMethodOp, AddPropertyOp)):
        return op.refs

    else:
        raise TypeError(op)
