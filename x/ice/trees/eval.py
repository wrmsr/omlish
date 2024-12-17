import itertools
import operator
import typing as ta

from omnibus import check
from omnibus import dataclasses as dc
from omnibus import dispatch

from . import nodes as no
from ..types import QualifiedName


StrMap = ta.Mapping[str, ta.Any]


class StmtEvaluator(dispatch.Class):

    def __init__(
            self,
    ) -> None:
        super().__init__()

        self._rels = RelationEvaluator()
        self._exprs = ExprEvaluator()

    eval = dispatch.property()

    def eval(self, node: no.Stmt) -> ta.Sequence[StrMap]:  # noqa
        raise TypeError(node)

    def eval(self, node: no.Select) -> ta.Sequence[StrMap]:  # noqa
        check.arg(dc.only(node, ['items', 'relations', 'where']))

        if list(node.items) == [no.AllSelectItem()]:
            if len(node.relations) != 1:
                raise ValueError(node.relations)
            rows = list(self._rels.eval(node.relations[0]))

            if node.where is not None:
                filtered_rows = []
                for row in rows:
                    if self._exprs.eval(node.where, row):
                        filtered_rows.append(row)
                rows = filtered_rows

            return rows

        elif all(isinstance(i, no.ExprSelectItem) for i in node.items) and not node.relations:
            row = {}
            for i in node.items:
                i = check.isinstance(i, no.ExprSelectItem)
                k = check.not_none(i.label).name
                v = self._exprs.eval(i.value, {})
                row[k] = v

            return [row]

        else:
            raise ValueError(node.items)


class RelationEvaluator(dispatch.Class):

    eval = dispatch.property()

    def eval(self, node: no.Relation) -> ta.Sequence[StrMap]:  # noqa
        raise TypeError(node)

    def eval(self, node: no.Join) -> ta.Sequence[StrMap]:  # noqa
        check.arg(dc.only(node, ['left', 'type', 'right']))
        check.arg(node.type == no.JoinType.DEFAULT)

        left = self.eval(node.left)
        right = self.eval(node.right)

        ret = []
        for l, r in itertools.product(left, right):
            ret.append({**l, **r})
        return ret

    def eval(self, node: no.Table) -> ta.Sequence[StrMap]:  # noqa
        if node.name.name == QualifiedName(['t0']):
            return [
                {'id': 1, 's': 'one'},
                {'id': 2, 's': 'two'},
            ]
        elif node.name.name == QualifiedName(['t1']):
            return [
                {'id': 1, 'i': 1},
                {'id': 2, 'i': 2},
            ]
        else:
            raise NameError(node.name.name)


OPS_BY_BINARY_OP = {
    no.BinaryOp.EQ: operator.eq,
    no.BinaryOp.NE: operator.ne,
    no.BinaryOp.NEX: operator.ne,
    no.BinaryOp.LT: operator.lt,
    no.BinaryOp.LTE: operator.le,
    no.BinaryOp.GT: operator.gt,
    no.BinaryOp.GTE: operator.ge,

    no.BinaryOp.ADD: operator.add,
    no.BinaryOp.SUB: operator.sub,
    no.BinaryOp.MUL: operator.mul,
    no.BinaryOp.DIV: operator.truediv,
    no.BinaryOp.MOD: operator.mod,
    no.BinaryOp.CONCAT: operator.add,
}


OPS_BY_UNARY_OP = {
    no.UnaryOp.NOT: operator.not_,

    no.UnaryOp.PLUS: operator.pos,
    no.UnaryOp.MINUS: operator.neg,
}


class ExprEvaluator(dispatch.Class):

    eval = dispatch.property()

    def eval(self, node: no.Expr, ns: StrMap) -> ta.Any:  # noqa
        raise TypeError(node)

    def eval(self, node: no.BinaryExpr, ns: StrMap) -> ta.Any:  # noqa
        if node.op == no.BinaryOp.AND:
            return self.eval(node.left, ns) and self.eval(node.right, ns)
        elif node.op == no.BinaryOp.OR:
            return self.eval(node.left, ns) or self.eval(node.right, ns)
        else:
            op = OPS_BY_BINARY_OP[node.op]
            left = self.eval(node.left, ns)
            right = self.eval(node.right, ns)
            return op(left, right)

    def eval(self, node: no.Primitive, ns: StrMap) -> ta.Any:  # noqa
        return node.value

    def eval(self, node: no.QualifiedNameNode, ns: StrMap) -> ta.Any:  # noqa
        return ns[node.name.dotted]

    def eval(self, node: no.UnaryOp, ns: StrMap) -> ta.Any:  # noqa
        op = OPS_BY_UNARY_OP[node.op]
        value = self.eval(node.value, ns)
        return op(value)
