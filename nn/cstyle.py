from .lazy import LazyBuffer
from .lazy import LazyOp
from .linear import LinearCodegen
from .linear import LinearCodegenOp


class CStyleCodegenOp(LinearCodegenOp):
    pass


class CstyleCodegen(LinearCodegen):
    def op(self, op: LazyOp, output: LazyBuffer) -> LinearCodegenOp:
        return CStyleCodegenOp(op, output)
