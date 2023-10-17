from __future__ import annotations

import typing as ta

from omlish import dataclasses as dc
import numpy as np

from . import ops
from .devices import Device
from .dtypes import ImageDType
from .dtypes import dtypes
from .execution import MemBuffer
from .execution import ScheduleItem
from .execution import get_lazyop_info
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


def fix_schedule_for_images(schedule: list[ScheduleItem]):
    # this is the fundamental fix, find unwritable or unreadable images and convert them to normal float32 (TODO: should it be float16?)
    for si in schedule:
        if (
                isinstance(si.out.dtype, ImageDType)
                and (
                    prod(si.out.shape) != prod(si.out.dtype.shape)
                    or not any(si.out.shape[x] % 4 == 0 for x in si.out.st.unit_stride_axes())
            )
        ):
            si.out.dtype = dtypes.float32
        for b in si.ast.get_lazyops():
            if not isinstance(b, ops.Mem):
                continue
            if (
                isinstance(si.inputs[b.arg.idx - 1].dtype, ImageDType)
                and (
                    b.arg.st.real_offset() % 4 != 0
                    or not any(b.arg.st.shape[x] % 4 == 0 for x in b.arg.st.unit_stride_axes())
                )
            ):
                si.inputs[b.arg.idx - 1].dtype = dtypes.float32

    # now fix up the schedule to reflect the new dtypes
    fixed_schedule: list[ScheduleItem] = []
    for si in schedule:
        ast = si.ast
        # fix input dtypes to match what they actually are
        replacements = {}
        for b in si.ast.get_lazyops():
            if not isinstance(b, ops.Mem):
                continue
            if b.arg.dtype != si.inputs[b.arg.idx - 1].dtype:
                replacements[b] = ops.Mem((), MemBuffer(b.arg.idx, si.inputs[b.arg.idx - 1].dtype, b.arg.st))
        if replacements:
            ast = ast.map_buffers(replacements)

        # fix the ops to create the output dtype
        if not isinstance(ast, ops.LoadOp):
            info = get_lazyop_info(ast)
            if info.dtype != si.out.dtype:
                ast = ops.Cast((ast,), (si.out.dtype, False))

        # put this in the fixed schedule
        fixed_schedule.append(dc.replace(si, ast=ast))
    return fixed_schedule


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
        # if DEBUG >= 3:
        #     print_tree(si.ast)
        if isinstance(si.ast, ops.LoadOp):
            # confirm the LoadOps are contiguous and in order
            for i, s in enumerate(si.ast.src):
                assert (
                    isinstance(s, LazyOp) and isinstance(s, ops.Mem) and s.arg.idx == i + 1 and s.arg.st.contiguous
                ), f"bad LoadOps src {i}: {s}"
            LOAD_OPS_DISPATCHER[type(si.ast)](si.out, *si.inputs)
        else:
            si.out.realized = Device[si.out.device].exec_ast(
                si.ast,
                output=si.out,
                inputs=si.inputs,
                var_vals=si.out.var_vals,
                **si.out._device_extra_args(),
            )
        del si.out.op
        for v in si.out.views: del v.op
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


def _realize_contiguous(buffer: LazyBuffer, src: LazyBuffer) -> None:
    # this is just a copy now, if it's not a copy schedule will handle it
    buffer.realized = src.realized
    assert buffer.dtype == src.dtype, f"contiguous dtype mismatch, expecting {buffer.dtype}, got {src.dtype}"


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
    ops.Contiguous: _realize_contiguous,
    ops.Custom: _realize_custom,
    ops.From: _realize_from,
}
