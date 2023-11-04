from __future__ import annotations

import typing as ta

import numpy as np

from . import ops
from .devices import Device
from .execution import ScheduleItem
from .features.image import fix_schedule_for_images
from .helpers import DEBUG
from .helpers import IMAGE
from .helpers import all_int
from .helpers import getenv
from .helpers import prod
from .lazy import LazyBuffer
from .ops import LazyOp
from .runtime.lib import RawBufferMapped
from .runtime.lib import RawBufferTransfer
from .runtime.ops_disk import RawDiskBuffer


P2P = getenv("P2P", 0)


# *** this is where things happen ***

def run_schedule(schedule: list[ScheduleItem]):
    # HACK: images can be not usable due to shape
    if IMAGE >= 2:
        schedule = fix_schedule_for_images(schedule)

    # NOTE: if you for loop the schedule it's slow because nothing frees
    while len(schedule):
        si = schedule.pop(0)

        # log_schedule_item(si)

        assert all(x.realized for x in si.inputs), "can't run schedule, some inputs aren't realized"

        if DEBUG >= 3:
            from .lazy import print_tree
            print_tree(si.ast)

        if isinstance(si.ast, ops.LoadOp):
            # confirm the LoadOps are contiguous and in order
            for i, s in enumerate(si.ast.src):
                assert (
                    isinstance(s, LazyOp)
                    and isinstance(s, ops.Mem)
                    and s.arg.idx == i + 1
                    and s.arg.st.contiguous
                ), f"bad LoadOps src {i}: {s}"
            LOAD_OPS_DISPATCHER[type(si.ast)](si.out, *si.inputs)

        else:
            si.out.realized = Device[si.out.device].exec_ast(
                si.ast,
                output=si.out,
                inputs=si.inputs,
                var_vals=si.var_vals,
                **si.out._device_extra_args(),
            )

        del si.out.op
        for v in si.out.views:
            del v.op

        assert (
            si.out.realized and isinstance(si.out.realized, Device[si.out.device].buffer)
        ), f"device mismatch on realized got {type(si.out.realized)} expected {si.out.device}"
        assert si.out.realized.dtype == si.out.dtype, "realized dtype is incorrect"


# *** zero op LoadOps ***


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


# *** one op LoadOps ***


def _realize_from(buffer: LazyBuffer, src: LazyBuffer) -> None:
    assert src.realized.size == buffer.st.size(), f"size mismatch on FROM {src.realized.size} != {buffer.st.size()}"
    assert src.st.contiguous and buffer.st.contiguous, "all must be contiguous for from"

    if DEBUG >= 3:
        print(f"*** copy {buffer.device} <- {src.device} size {src.realized.size} dtype {src.realized.dtype}")

    # TODO: make this generic
    if isinstance(src.realized, RawDiskBuffer) and issubclass(Device[buffer.device].buffer, RawBufferMapped):
        assert all_int(buffer.shape), "does not support symbolic shape"
        buffer.realized = Device[buffer.device].buffer(prod(buffer.shape), buffer.dtype, **buffer._device_extra_args())
        src.realized.readinto(ta.cast(RawBufferMapped, buffer.realized)._buffer())

    elif (
            isinstance(src.realized, RawBufferTransfer)
            and issubclass(Device[buffer.device].buffer, RawBufferTransfer)
            and P2P >= 1
    ):
        buffer.realized = ta.cast(RawBufferTransfer, Device[buffer.device].buffer).transfer(
            src.realized,
            buffer.shape,
            buffer.dtype,
            **buffer._device_extra_args(),
        )

    else:
        # TODO: schedule this as FROM to go to CPU, and a FROM to go to device
        buffer.realized = Device[buffer.device].buffer.fromCpu(src.realized.toCpu(), **buffer._device_extra_args())


# *** n op LoadOps ***

def _realize_custom(buffer: LazyBuffer, *inputs: LazyBuffer) -> None:
    buffer.realized = buffer.op.arg(buffer, *inputs)


LOAD_OPS_DISPATCHER: dict[type[ops.LoadOp], ta.Callable] = {
    ops.Empty: _realize_empty,
    ops.Rand: _realize_rand,
    ops.Custom: _realize_custom,
    ops.From: _realize_from,
}
