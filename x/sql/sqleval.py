import itertools
import operator
import typing as ta

from omlish import check
from omlish import dataclasses as dc
from omlish import dispatch
from omlish.sql import qn
from omlish.sql import queries as no


StrMap: ta.TypeAlias = ta.Mapping[str, ta.Any]


##


class StmtEvaluator:
    def __init__(self) -> None:
        super().__init__()

        self._rels = RelationEvaluator()
        self._exprs = ExprEvaluator()

    @dispatch.method
    def eval(self, node: no.Stmt) -> ta.Sequence[StrMap]:
        raise TypeError(node)

    @eval.register
    def _eval_select(self, node: no.Select) -> ta.Sequence[StrMap]:
        check.arg(dc.only(node, 'items', 'from_', 'where'))

        if len(node.items) == 1 and isinstance(node.items[0], no.AllSelectItem):
            rows = list(self._rels.eval(node.from_))

            if node.where is not None:
                filtered_rows = []
                for row in rows:
                    if self._exprs.eval(node.where, row):
                        filtered_rows.append(row)
                rows = filtered_rows

            return rows

        elif all(isinstance(i, no.ExprSelectItem) for i in node.items) and node.from_ is None:
            row = {}
            for i in node.items:
                i = check.isinstance(i, no.ExprSelectItem)
                k = check.not_none(i.a).s
                v = self._exprs.eval(i.v, {})
                row[k] = v

            return [row]

        else:
            raise ValueError(node.items)


##


class RelationEvaluator:
    @dispatch.method
    def eval(self, node: no.Relation) -> ta.Sequence[StrMap]:
        raise TypeError(node)

    @eval.register
    def _eval_join(self, node: no.Join) -> ta.Sequence[StrMap]:
        check.arg(dc.only(node, 'k', 'l', 'r'))
        check.arg(node.k == no.JoinKind.DEFAULT)

        left = self.eval(node.l)
        right = self.eval(node.r)

        ret = []
        for l, r in itertools.product(left, right):
            ret.append({**l, **r})
        return ret

    @eval.register
    def _eval_table(self, node: no.Table) -> ta.Sequence[StrMap]:
        if node.n.qn == qn('t0'):
            return [
                {'id': 1, 's': 'one'},
                {'id': 2, 's': 'two'},
            ]
        elif node.n.qn == qn('t1'):
            return [
                {'id': 1, 'i': 1},
                {'id': 2, 'i': 2},
            ]
        else:
            raise NameError(node.n.qn)


##


OPS_BY_BINARY_OP = {
    no.BinaryOps.EQ: operator.eq,
    no.BinaryOps.NE: operator.ne,
    no.BinaryOps.LT: operator.lt,
    no.BinaryOps.LE: operator.le,
    no.BinaryOps.GT: operator.gt,
    no.BinaryOps.GE: operator.ge,

    no.BinaryOps.ADD: operator.add,
    no.BinaryOps.SUB: operator.sub,
    no.BinaryOps.MUL: operator.mul,
    no.BinaryOps.DIV: operator.truediv,
    no.BinaryOps.MOD: operator.mod,
    no.BinaryOps.CONCAT: operator.add,
}


OPS_BY_UNARY_OP = {
    no.UnaryOps.NOT: operator.not_,

    no.UnaryOps.POS: operator.pos,
    no.UnaryOps.NEG: operator.neg,
}


class ExprEvaluator:
    @dispatch.method
    def eval(self, node: no.Expr, ns: StrMap) -> ta.Any:
        raise TypeError(node)

    @eval.register
    def _eval_binary(self, node: no.Binary, ns: StrMap) -> ta.Any:
        op = OPS_BY_BINARY_OP[node.op]
        left = self.eval(node.l, ns)
        right = self.eval(node.r, ns)
        return op(left, right)

    @eval.register
    def _eval_multi(self, node: no.Multi, ns: StrMap) -> ta.Any:
        if node.k == no.MultiKind.AND:
            return all(self.eval(e, ns) for e in node.es)
        elif node.k == no.MultiKind.OR:
            return any(self.eval(e, ns) for e in node.es)
        else:
            raise ValueError(node.k)

    @eval.register
    def _eval_literal(self, node: no.Literal, ns: StrMap) -> ta.Any:
        return node.v

    @eval.register
    def _eval_name_expr(self, node: no.NameExpr, ns: StrMap) -> ta.Any:
        return ns[node.n.qn.dotted]

    @eval.register
    def _eval_unary(self, node: no.Unary, ns: StrMap) -> ta.Any:
        op = OPS_BY_UNARY_OP[node.op]
        value = self.eval(node.v, ns)
        return op(value)
