import functools
import typing as ta

from ... import nodes as no
from .... import check
from .... import dataclasses as dc
from ..types import Args
from ..types import Macro
from ..types import Xlat
from .default import DEFAULT_MACROS


class NamedMacro(dc.Frozen, allow_setattr=True):
    name: str
    fn: Macro
    arity: ta.Optional[int] = None

    def __call__(self, xlat: Xlat, args: Args) -> no.Node:
        return self.fn(xlat, args)


def named_macro(
        name: ta.Optional[str] = None,
        *,
        default: bool = False,
        register_on: ta.Iterable[ta.MutableSequence[Macro]] = (),
        arity: ta.Optional[int] = None,
) -> ta.Callable[..., Macro]:
    def inner(fn):
        m = NamedMacro(name if name is not None else fn.__name__, fn, arity=arity)
        functools.update_wrapper(m, fn)
        for r in register_on:
            r.append(m)
        return m

    if name is not None:
        check.non_empty_str(name)
    register_on = list(register_on)
    if default:
        register_on.append(DEFAULT_MACROS)
    for r in register_on:
        check.not_isinstance(r, ta.Mapping)
    return inner


@named_macro('def', default=True)
def def_(xlat: Xlat, args: Args) -> no.Node:
    args = list(args)
    name = no.Ident(args.pop(0))
    fnargs = no.Args([no.Arg(no.Ident(a)) for a in args.pop(0)])
    body = []
    for b in args:
        xb = xlat(b)
        if isinstance(xb, no.Stmt):
            xs = xb
        elif isinstance(xb, no.Expr):
            xs = no.ExprStmt(xb)
        else:
            raise TypeError(xb)
        body.append(xs)
    return no.Fn(
        name,
        fnargs,
        body,
    )


@named_macro('return', default=True)
def return_(xlat: Xlat, args: Args) -> no.Node:
    args = list(args)
    if args:
        value = xlat(args.pop(0))
    else:
        value = None
    check.empty(args)
    return no.Return(value)


def bin_op_macro(op: no.BinOp, xlat: Xlat, args: Args) -> no.Node:
    left, right = map(xlat, args)
    return no.BinExpr(
        left,
        op,
        right,
    )


def bool_op_macro(op: no.BoolOp, xlat: Xlat, args: Args) -> no.Node:
    left, right = map(xlat, args)
    return no.BoolExpr(
        left,
        op,
        right,
    )


def cmp_op_macro(op: no.CmpOp, xlat: Xlat, args: Args) -> no.Node:
    left, right = map(xlat, args)
    return no.CmpExpr(
        left,
        op,
        right,
    )


def unary_op_macro(op: no.UnaryOp, xlat: Xlat, args: Args) -> no.Node:
    value = xlat(check.single(args))
    return no.UnaryExpr(
        op,
        value,
    )


check.not_empty([
    named_macro(op.glyph, default=True, arity=arity)(functools.partial(fn, op))
    for ns, fn, arity in [
        (no.BinOps, bin_op_macro, 2),
        (no.BoolOps, bool_op_macro, 2),
        (no.CmpOps, cmp_op_macro, 2),
        (no.UnaryOps, unary_op_macro, 1),
    ]
    for n in ns for op in [ns(n)]
])


@named_macro('[', default=True)
def get_item(xlat: Xlat, args: Args) -> no.Node:
    args = list(args)
    obj = xlat(args.pop(0))
    idx = xlat(check.single(args))
    return no.GetItem(
        obj,
        idx,
    )


@named_macro('[=', default=True)
def set_item(xlat: Xlat, args: Args) -> no.Node:
    args = list(args)
    obj = xlat(args.pop(0))
    idx = xlat(args.pop(0))
    value = xlat(check.single(args))
    return no.SetItem(
        obj,
        idx,
        value,
    )
