from .. import nodes as no
from .. import eval as sev


def test_eval():
    assert sev.Evaluator()(no.Const(420), sev.MutableEvalContext())[0] == 420
    assert sev.Evaluator()(no.BinExpr(no.Const(420), no.BinOps.ADD, no.Const(421)), sev.MutableEvalContext())[0] == 841
