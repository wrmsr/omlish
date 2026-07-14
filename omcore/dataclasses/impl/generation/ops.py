import dataclasses as dc
import typing as ta

from .... import check
from .... import lang
from ...clsattrs import IfAttrPresent
from .globals import FnGlobal
from .idents import IDENT_PREFIX


T = ta.TypeVar('T')

RefT = ta.TypeVar('RefT', bound='Ref')


##


class _OpRef(ta.NamedTuple, ta.Generic[T]):
    name: str


@ta.final
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

    #

    @classmethod
    def numbered(cls, limit: int) -> ta.Callable[[str, int], OpRef[T]]:
        z = len(str(limit))

        def inner(s: str, i: int) -> OpRef[T]:
            check.arg(i < limit)

            return OpRef(s.format(i=str(i).zfill(z)))

        return inner


##


OpRefMap: ta.TypeAlias = ta.Mapping[OpRef, ta.Any]

Ref: ta.TypeAlias = OpRef | FnGlobal


def add_ref(ref: RefT, refs: ta.MutableSet[Ref]) -> RefT:
    refs.add(ref)
    return ref


##


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

    if_present: IfAttrPresent = dc.field(default='raise', kw_only=True)


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
