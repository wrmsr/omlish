"""
https://github.com/wrmsr/omlish/blob/f80afa5bf7f325ecf76d6bb7539818bb79e51806/x/omni/nodal/tests/SubsTest.java
"""
import abc
import dataclasses as dc
import typing as ta


C = ta.TypeVar('C')
R = ta.TypeVar('R')


# A

A = ta.TypeVar('A')


class ANode(abc.ABC, ta.Generic[A, C, R]):
    @abc.abstractmethod
    def accept_a_visitor(self, visitor: 'AVisitor[A, C, R]', ctx: C) -> R:
        raise NotImplementedError


class AVisitor(ta.Generic[A, C, R]):
    def visit_a_node(self, node: 'ANode[A]', ctx: C) -> R:
        raise RuntimeError(node)

    def visit_a_add(self, node: 'AAdd[A]', ctx: C) -> R:
        return self.visit_a_node(node, ctx)

    def visit_a_const(self, node: 'AConst[A]', ctx: C) -> R:
        return self.visit_a_node(node, ctx)


@dc.dataclass(frozen=True)
class AAdd(ANode[A]):
    left: ANode[A]
    right: ANode[A]

    def accept_a_visitor(self, visitor: AVisitor[A, R, C], ctx: C) -> R:
        return visitor.visit_a_add(self, ctx)


@dc.dataclass(frozen=True)
class AConst(ANode[A]):
    val: int

    def accept_a_visitor(self, visitor: AVisitor[A, R, C], ctx: C) -> R:
        return visitor.visit_a_const(self, ctx)


# B

B = ta.TypeVar('B')


class BNode(ANode['BNode'], abc.ABC, ta.Generic[C, R]):
    def accept_a_visitor(self, visitor: AVisitor['BNode', C, R], ctx: C) -> R:
        return self.accept_b_visitor(visitor, ctx)

    @abc.abstractmethod
    def accept_b_visitor(self, visitor: 'BVisitor[C, R]', ctx: C) -> R:
        raise NotImplementedError


class BVisitor(AVisitor[BNode, C, R]):
    def visit_b_node(self, node: BNode, ctx: C) -> R:
        return self.visit_a_node(node, ctx)

    def visit_b_add(self, node: 'BAdd', ctx: C) -> R:
        return self.visit_a_add(node, ctx)

    def visit_b_const(self, node: 'BConst', ctx: C) -> R:
        return self.visit_a_const(node, ctx)

    def visit_b_mul(self, node: 'BMul', ctx: C) -> R:
        return self.visit_b_node(node, ctx)


@dc.dataclass(frozen=True)
class BAdd(AAdd[BNode]):
    def accept_b_visitor(self, visitor: BVisitor[C, R], ctx: C) -> R:
        return visitor.visit_b_add(self, ctx)


@dc.dataclass(frozen=True)
class BConst(AConst[BNode]):
    def accept_b_visitor(self, visitor: BVisitor[C, R], ctx: C) -> R:
        return visitor.visit_b_const(self, ctx)


@dc.dataclass(frozen=True)
class BMul(BNode):
    left: BNode
    right: BNode

    def accept_b_visitor(self, visitor: BVisitor[C, R], ctx: C) -> R:
        return visitor.visit_b_mul(self, ctx)


#

"""
## AEval

public static class AEval<A>
        implements AVisitor<A, Integer, Void>
{
    @Override
    public Integer visitAAdd(AAdd<A> node, Void ctx)
    {
        return node.left.acceptAVisitor(this, ctx) + node.right.acceptAVisitor(this, ctx);
    }

    @Override
    public Integer visitAConst(AConst<A> node, Void ctx)
    {
        return node.val;
    }
}

public static <A> int aEval(ANode<A> node)
{
    return node.acceptAVisitor(new AEval<A>(), null);
}


## BEval

public static class BEval
        extends AEval<BNode>
        implements BVisitor<Integer, Void>
{
    @Override
    public Integer visitBMul(BMul node, Void ctx)
    {
        return node.left.acceptBVisitor(this, ctx) * node.right.acceptBVisitor(this, ctx);
    }
}

public static int bEval(BNode node)
{
    return node.acceptBVisitor(new BEval(), null);
}


##

@Test
public void testSubs()
        throws Throwable
{
    assertEquals(aEval(aConst(1)), 1);
    assertEquals(aEval(aAdd(aConst(1), aConst(2))), 1 + 2);
    assertEquals(bEval(bMul(bConst(2), bConst(3))), 2 * 3);
    assertEquals(bEval(bMul(bConst(2), bAdd(bConst(3), bConst(4)))), 2 + (3 * 4));
    assertEquals(bEval(bMul(bConst(2), bAdd(bConst(3), bMul(bConst(4), bConst(5))))), 2 * (3 + (4 * 5)));
}
"""