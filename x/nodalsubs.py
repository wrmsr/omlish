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


class ANode(abc.ABC, ta.Generic[A]):
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

    def accept_a_visitor(self, visitor: AVisitor[A, C, R], ctx: C) -> R:
        return visitor.visit_a_add(self, ctx)


@dc.dataclass(frozen=True)
class AConst(ANode[A]):
    val: int

    def accept_a_visitor(self, visitor: AVisitor[A, C, R], ctx: C) -> R:
        return visitor.visit_a_const(self, ctx)


# B


class BNode(ANode['BNode'], abc.ABC):
    def accept_a_visitor(self, visitor: AVisitor['BNode', C, R], ctx: C) -> R:
        if not isinstance(visitor, BVisitor):
            raise TypeError(visitor)
        return self.accept_b_visitor(ta.cast(BVisitor[C, R], visitor), ctx)

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
class BAdd(AAdd[BNode], BNode):
    def accept_b_visitor(self, visitor: BVisitor[C, R], ctx: C) -> R:
        return visitor.visit_b_add(self, ctx)


@dc.dataclass(frozen=True)
class BConst(AConst[BNode], BNode):
    def accept_b_visitor(self, visitor: BVisitor[C, R], ctx: C) -> R:
        return visitor.visit_b_const(self, ctx)


@dc.dataclass(frozen=True)
class BMul(BNode):
    left: BNode
    right: BNode

    def accept_b_visitor(self, visitor: BVisitor[C, R], ctx: C) -> R:
        return visitor.visit_b_mul(self, ctx)


# AEval

class AEval(AVisitor[A, None, int]):
    def visit_a_add(self, node: 'AAdd[A]', ctx: None) -> int:
        return node.left.accept_a_visitor(self, ctx) + node.right.accept_a_visitor(self, ctx)

    def visit_a_const(self, node: 'AConst[A]', ctx: None) -> int:
        return node.val


def a_eval(node: ANode[A]) -> int:
    return node.accept_a_visitor(AEval(), None)


# BEval

class BEval(AEval[BNode], BVisitor[None, int]):
    def visit_b_mul(self, node: BMul, ctx: None) -> int:
        return node.left.accept_b_visitor(self, ctx) * node.right.accept_b_visitor(self, ctx)


def b_eval(node: BNode) -> int:
    return node.accept_b_visitor(BEval(), None)


#

def _main() -> None:
    assert a_eval(AConst(1)) == 1
    assert a_eval(AAdd(AConst(1), AConst(2))) == 1 + 2
    assert b_eval(BMul(BConst(2), BConst(3))) == 2 * 3
    assert b_eval(BMul(BConst(2), BAdd(BConst(3), BConst(4)))) == 2 + (3 * 4)
    assert b_eval(BMul(BConst(2), BAdd(BConst(3), BMul(BConst(4), BConst(5))))) == 2 * (3 + (4 * 5))


if __name__ == '__main__':
    _main()
