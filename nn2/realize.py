from __future__ import annotations

import typing as ta

import numpy as np

from . import ops
from .devices import Device
from .helpers import DEBUG
from .helpers import all_int
from .helpers import getenv
from .helpers import prod
from .lazy import LazyBuffer
from .ops import LazyOp
from .runtime.lib import RawBufferMapped
from .runtime.lib import RawBufferTransfer
from .runtime.ops_disk import RawDiskBuffer


P2P = getenv("P2P", 0)


def run_schedule(schedule: list[tuple[LazyOp, LazyBuffer, tuple[LazyBuffer, ...]]]):
    # NOTE: if you for loop the schedule it's slow because nothing frees
    while len(schedule):
        op, out, buffers = schedule.pop(0)
        # log_schedule_item(op, out, buffers)
        if DEBUG >= 3:
            from .helpers import print_tree
            print_tree(op)

        if isinstance(op, ops.LoadOp):
            LOAD_OPS_DISPATCHER[type(op)](out)
            # TODO: why can't we delete these ops?
        else:
            out.realized = Device[out.device].exec_ast(
                op,
                output=out,
                inputs=[x.realized for x in buffers],
                var_vals=out.var_vals,
                **out._device_extra_args(),
            )
            del out.op
            for v in out.views:
                del v.op

        assert out.realized and isinstance(
            out.realized, Device[out.device].buffer
        ), f"device mismatch on realized got {type(out.realized)} expected {out.device}"

        assert out.realized.dtype == out.dtype, "realized dtype is incorrect"


def _realize_contiguous(buffer: LazyBuffer) -> None:
    # this is just a copy now, if it's not a copy schedule will handle it
    src = ta.cast(LazyBuffer, buffer.op.src[0])
    buffer.realized = src.realized
    assert (
            buffer.dtype == src.dtype
    ), f"contiguous dtype mismatch, expecting {buffer.dtype}, got {src.dtype}"


def _realize_custom(buffer: LazyBuffer) -> None:
    # this needs to immediately realize
    buffer.realized = buffer.op.arg(buffer, *[x.realize() for x in buffer.op.src])


def _realize_from(buffer: LazyBuffer) -> None:
    rawbuf = ta.cast(LazyBuffer, buffer.op.src[0]).contiguous().realize()
    assert rawbuf.realized, "realize failed?"
    if DEBUG >= 3:
        print(
            f"*** copy {buffer.device} <- {rawbuf.device} size {rawbuf.realized.size} dtype {rawbuf.realized.dtype}"
        )

    # TODO: make this generic
    if isinstance(rawbuf.realized, RawDiskBuffer) and issubclass(
            Device[buffer.device].buffer, RawBufferMapped
    ):
        assert all_int(buffer.shape), "does not support symbolic shape"
        buffer.realized = Device[buffer.device].buffer(
            prod(buffer.shape),
            buffer.dtype,
            **buffer._device_extra_args()
        )
        rawbuf.prepare_transfer().readinto(
            ta.cast(RawBufferMapped, buffer.realized)._buffer()
        )

    elif (
            isinstance(rawbuf.realized, RawBufferTransfer)
            and issubclass(Device[buffer.device].buffer, RawBufferTransfer)
            and P2P >= 1
    ):
        buffer.realized = ta.cast(
            RawBufferTransfer, Device[buffer.device].buffer
        ).transfer(
            rawbuf.realized,
            buffer.shape,
            buffer.dtype,
            **buffer._device_extra_args()
        )

    else:
        buffer.realized = Device[buffer.device].buffer.fromCpu(
            rawbuf.toCpu(),
            **buffer._device_extra_args()
        )


def _realize_empty(buffer: LazyBuffer) -> None:
    assert all_int(buffer.shape), "does not support symbolic shape"
    buffer.realized = Device[buffer.device].buffer(
        prod(buffer.shape), buffer.dtype, **buffer._device_extra_args()
    )


def _realize_rand(buffer: LazyBuffer) -> None:
    assert all_int(buffer.shape), "does not support symbolic shape"

    rng = np.random.default_rng(buffer.op.arg)

    buffer.realized = Device[buffer.device].buffer.fromCpu(
        rng.random(size=prod(buffer.shape), dtype=np.float32).astype(dtype=buffer.dtype.np, copy=False),
        **buffer._device_extra_args(),
    )


LOAD_OPS_DISPATCHER: dict[type[ops.LoadOp], ta.Callable] = {
    ops.Contiguous: _realize_contiguous,
    ops.Custom: _realize_custom,
    ops.From: _realize_from,
    ops.Empty: _realize_empty,
    ops.Rand: _realize_rand,
}
