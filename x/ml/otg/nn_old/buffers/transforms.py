import typing as ta

from omlish import check

from .. import ops
from ..lazy import Lazy
from .buffers import Buffer
from .buffers import elementwise_op


def replace_with_movement_ops(
        y: Lazy,
        lst: ta.List[ta.Tuple[ta.Type[ops.MovementOp], ta.Any]],
) -> 'Buffer':
    if isinstance(y, Buffer):
        for op, arg in lst:
            y = y.movement_op(op, arg)
        return y

    elif isinstance(y, ops.Op):
        check.isinstance(y, (ops.BinaryOp, ops.UnaryOp))

        return elementwise_op(
            type(y),  # type: ignore
            *[replace_with_movement_ops(z, lst) for z in y.srcs],
            *y.args
        )

    else:
        raise TypeError(y)


def push_movement_ops(srcs: ta.Sequence[Buffer]) -> ta.Sequence[Buffer]:
    new_srcs = []

    for x in srcs:
        mops: ta.List[ta.Tuple[ta.Type[ops.MovementOp], ta.Any]] = []
        bx = x

        # backwalk all the movement ops. don't push PAD or EXPAND
        while (
                bx._realized is None
                and isinstance(bx.op, ops.MovementOp)
                and type(bx.op) != ops.Expand
                and (
                        type(bx.op) != ops.Pad
                        # or SHUFFLE_PAD_OPS
                )
                and len(bx._children) <= 1
        ):
            mops.append((type(check.isinstance(bx.op, ops.MovementOp)), check.single(bx.op.args)))
            bx = bx.op.srcs[0].as_buffer()

        # NOTE: can't push pads past anything where f(0, 0) != 0 or f(0) != 0
        unsafe_pad_ops = {ops.Div, ops.CmpLt, ops.Log2, ops.Exp2, ops.Recip}
        if (
                bx._realized is None
                and isinstance(bx.op, ops.BinaryOp)
                and len(bx._children) <= 1
                and len(mops)
                and (
                all(x[0] != ops.Pad for x in mops) or
                all(type(x) not in unsafe_pad_ops for x in bx.op.ops)
        )
        ):
            new_srcs.append(replace_with_movement_ops(bx.op, mops[::-1]))
        else:
            new_srcs.append(x)

    return tuple(new_srcs)
