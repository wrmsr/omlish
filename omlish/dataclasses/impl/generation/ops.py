import dataclasses as dc
import typing as ta

from .... import lang
from .globals import FnGlobal
from .idents import IDENT_PREFIX


T = ta.TypeVar('T')


##


class _OpRef(ta.NamedTuple, ta.Generic[T]):
    name: str


class OpRef(_OpRef[T]):
    def __repr__(self) -> str:
        return f'OpRef(name={self.name!r})'

    #

    _ident: str

    def ident(self) -> str:
        try:
            return self._ident
        except AttributeError:
            pass

        ident = IDENT_PREFIX + self.name.replace('.', '__')
        self._ident = ident  # noqa
        return ident


##


OpRefMap: ta.TypeAlias = ta.Mapping[OpRef, ta.Any]

Ref: ta.TypeAlias = OpRef | FnGlobal


##


IfAttrPresent: ta.TypeAlias = ta.Literal['skip', 'replace', 'error']


@dc.dataclass(frozen=True)
class Op(lang.Abstract):
    pass


@dc.dataclass(frozen=True)
class SetAttrOp(Op):
    name: str
    value: Ref | ta.Any

    if_present: IfAttrPresent = dc.field(default='replace', kw_only=True)


@dc.dataclass(frozen=True)
class AddMethodOp(Op):
    name: str
    src: str
    refs: frozenset[Ref] = dc.field(default=frozenset())

    if_present: IfAttrPresent = dc.field(default='error', kw_only=True)


@dc.dataclass(frozen=True)
class AddPropertyOp(Op):
    name: str
    get_src: str | None = None
    set_src: str | None = None
    del_src: str | None = None
    refs: frozenset[Ref] = frozenset()


##


def get_op_refs(op: Op) -> frozenset[Ref]:
    if isinstance(op, SetAttrOp):
        if isinstance(v := op.value, (OpRef, FnGlobal)):
            return frozenset([v])
        else:
            return frozenset()

    elif isinstance(op, (AddMethodOp, AddPropertyOp)):
        return op.refs

    else:
        raise TypeError(op)
