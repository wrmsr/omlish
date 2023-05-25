import typing as ta

from omlish import lang
from omlish.dev import pytest as ptu
import numpy as np

if ta.TYPE_CHECKING:
    import pyopencl as cl
else:
    cl = lang.proxy_import('pyopencl')


@ptu.skip_if_cant_import('pyopencl')
def test_opencl():
    dev_lsts: ta.List[ta.List[cl.Device]] = [
        ds
        for dt in (cl.device_type.GPU, cl.device_type.CPU)
        for ds in [plat.get_devices(device_type=dt) for plat in cl.get_platforms()]
        if ds
    ]

    cl_ctx: cl.Context = cl.Context(devices=dev_lsts[0])

    cl_queue: ta.List[cl.CommandQueue] = [
        cl.CommandQueue(
            cl_ctx,
            device=dev,
            properties=cl.command_queue_properties.PROFILING_ENABLE,
        )
        for dev in cl_ctx.devices
    ]

    ##

    size = 8
    item_size = 4
    device = 0
    x = np.arange(8, dtype=np.float32)

    buf = cl.Buffer(cl_ctx, cl.mem_flags.READ_WRITE, size * item_size)

    cl.enqueue_copy(cl_queue[device], buf, x, is_blocking=False)

    # e = self.clprg(
    #     cl_queue[device], global_size, local_size, *cl_bufs
    # )

    cl.enqueue_copy(cl_queue[buf.device], x, buf, is_blocking=True)
