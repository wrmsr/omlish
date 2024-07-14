"""
TODO:
 - 'non-final' Nodal base classes take a self-var
 - base hierarchy no longer final/sealed but that's also the whole point..
  - special handling of sealing? enforce subtree has subtypes of all?
 - generate mapper between AFoo and BFoo
 - transformers need to lift
"""
import dataclasses as dc
import typing as ta


###


VarANode = ta.TypeVar('VarANode', bound='ANode')


class ANode(ta.Generic[VarANode]):
    pass


@dc.dataclass()
class AConst(ANode[VarANode]):
    val: int


@dc.dataclass()
class AAdd(ANode[VarANode]):
    left: VarANode
    right: VarANode

    def __post_init__(self):
        if not isinstance(self.left, ANode):
            raise TypeError(self.left)
        if not isinstance(self.right, ANode):
            raise TypeError(self.right)


###


class BNode(ANode['BNode']):
    pass


class BConst(AConst[BNode], BNode):
    pass


class BAdd(AAdd[BNode], BNode):
    pass


@dc.dataclass()
class BMul(BNode):
    left: BNode
    right: BNode

    def __post_init__(self):
        if not isinstance(self.left, BNode):
            raise TypeError(self.left)
        if not isinstance(self.right, BNode):
            raise TypeError(self.right)


###


class ShittyVisitor:
    def __call__(self, obj, *args, **kwargs):
        bfn, bty = None, None
        for an in dir(self):
            if not an.startswith('visit_'):
                continue
            afn = getattr(self, an)
            aty = afn.__annotations__[afn.__code__.co_varnames[1]]
            if not isinstance(obj, aty):
                continue
            if bfn is not None and not issubclass(aty, bty):
                if not issubclass(bty, aty):
                    raise TypeError(f'Ambiguous dispatch: {obj} {aty} {bty}')
                continue
            bfn, bty = afn, aty
        if bfn is None:
            raise TypeError(obj)
        return bfn(obj, *args, **kwargs)


class AEval(ShittyVisitor):
    def visit_const(self, obj: AConst) -> int:
        return obj.val

    def visit_add(self, obj: AAdd) -> int:
        return self(obj.left) + self(obj.right)


class BEval(AEval):
    def visit_mul(self, obj: BMul) -> int:
        return self(obj.left) * self(obj.right)


###


def test_subs():
    assert AEval()(AConst(1)) == 1
    assert AEval()(AAdd(AConst(1), AConst(2))) == 1 + 2
    assert BEval()(AAdd(AConst(1), AConst(2))) == 1 + 2
    assert BEval()(BMul(BConst(2), BConst(3))) == 2 * 3
    assert BEval()(BMul(BConst(2), BAdd(BConst(3), BConst(4)))) == 2 * (3 + 4)
    assert BEval()(BMul(BConst(2), BAdd(BConst(3), BMul(BConst(4), BConst(5))))) == 2 * (3 + (4 * 5))
