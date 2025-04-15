import abc
import dataclasses as dc
import typing as ta

from .idents import IDENT_PREFIX


T = ta.TypeVar('T')


##


class OpRef(ta.NamedTuple, ta.Generic[T]):
    name: str

    def ident(self) -> str:
        return IDENT_PREFIX + self.name.replace( '.', '__')


OpRefMap: ta.TypeAlias = ta.Mapping[OpRef, ta.Any]


##


IfAttrPresent: ta.TypeAlias = ta.Literal['skip', 'replace', 'error']


@dc.dataclass(frozen=True)
class Op(abc.ABC):  # noqa
    pass


@dc.dataclass(frozen=True)
class SetAttrOp(Op):
    name: str
    value: OpRef | ta.Any

    if_present: IfAttrPresent = dc.field(default='replace', kw_only=True)


@dc.dataclass(frozen=True)
class AddMethodOp(Op):
    name: str
    src: str
    refs: frozenset[OpRef] = dc.field(default=frozenset())

    if_present: IfAttrPresent = dc.field(default='error', kw_only=True)


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
