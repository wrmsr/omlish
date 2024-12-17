from omnibus import check
from omnibus import dataclasses as dc
from omnibus import dispatch
import sqlalchemy as sa
import sqlalchemy.sql.elements

from . import nodes as no


Visitable = sa.sql.elements.Visitable


class Transmuter(dispatch.Class):

    binary_op_handlers = {
        no.BinaryOp.AND: lambda l, r: sa.and_(l, r),
        no.BinaryOp.OR: lambda l, r: sa.or_(l, r),

        no.BinaryOp.EQ: lambda l, r: l == r,
        no.BinaryOp.NE: lambda l, r: l != r,
        no.BinaryOp.NEX: lambda l, r: l != r,
        no.BinaryOp.LT: lambda l, r: l < r,
        no.BinaryOp.LTE: lambda l, r: l <= r,
        no.BinaryOp.GT: lambda l, r: l > r,
        no.BinaryOp.GTE: lambda l, r: l >= r,

        no.BinaryOp.ADD: lambda l, r: l + r,
        no.BinaryOp.SUB: lambda l, r: l - r,
        no.BinaryOp.MUL: lambda l, r: l * r,
        no.BinaryOp.DIV: lambda l, r: l / r,
        no.BinaryOp.MOD: lambda l, r: l % r,
        no.BinaryOp.CONCAT: lambda l, r: sa.func.concat(l, r),
    }

    transmute = dispatch.property()

    def transmute(self, node: no.Node) -> Visitable:  # noqa
        raise TypeError(node)

    def transmute(self, node: no.AliasedRelation) -> Visitable:  # noqa
        check.arg(not node.columns)
        return self.transmute(node.relation).alias(node.alias.name)

    def transmute(self, node: no.BinaryExpr) -> Visitable:  # noqa
        l = self.transmute(node.left)
        r = self.transmute(node.right)
        return self.binary_op_handlers[node.op](l, r)  # noqa

    def transmute(self, node: no.Integer) -> Visitable:  # noqa
        return sa.literal(node.value)

    def transmute(self, node: no.Join) -> Visitable:  # noqa
        check.arg(not node.condition)
        l = self.transmute(node.left)
        r = self.transmute(node.right)
        return sa.join(l, r, sa.literal(True))

    def transmute(self, node: no.QualifiedNameNode) -> Visitable:  # noqa
        return sa.literal_column(node.name.dotted)

    def transmute(self, node: no.Select) -> Visitable:  # noqa
        check.arg(dc.only(node, ['items', 'relations', 'where']))

        items = []
        for i in node.items:
            if isinstance(i, no.ExprSelectItem):
                v = self.transmute(i.value)
                if i.label:
                    v = v.label(i.label.name)
                items.append(v)
            elif isinstance(i, no.AllSelectItem):
                items.append('*')
            else:
                raise TypeError(i)

        rels = []
        for r in node.relations:
            rels.append(self.transmute(r))

        if node.where:
            where = self.transmute(node.where)
        else:
            where = None

        stmt = sa.select(items)
        if rels:
            rel = rels[0]
            for cur_rel in rels[1:]:
                # FIXME: general purpose 'true' element, true in pg, 1 in mysql, ...
                rel = sa.join(rel, cur_rel, sa.text('true'))  # sa.literal(True)
            stmt = stmt.select_from(rel)
        if where is not None:
            stmt = stmt.where(where)
        return stmt

    def transmute(self, node: no.Table) -> Visitable:  # noqa
        return sa.table(node.name.name.dotted)


def transmute(node: no.Node) -> Visitable:
    return Transmuter().transmute(node)
