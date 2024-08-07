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
    x2 = np.zeros_like(x)

    print(x)

    cl_buf = cl.Buffer(cl_ctx, cl.mem_flags.READ_WRITE, size * item_size)
    cl_buf2 = cl.Buffer(cl_ctx, cl.mem_flags.READ_WRITE, size * item_size)

    cl.enqueue_copy(cl_queue[device], cl_buf, x, is_blocking=False)

    ##

    name = 'E_8'
    prg = """
__kernel void E_8(__global float* data0, const __global float* data1) {
{ int gidx0 = get_global_id(0);  /* 8 */
  float val1_0 = data1[gidx0];
  float val2_0 = 2.0f;
  float alu0 = (val1_0*val2_0);
  data0[gidx0] = alu0;
} /* global */
}
"""

    cl_prg = cl.Program(cl_ctx, prg)
    _cl_bin = cl_prg.build()
    cl_bin = getattr(_cl_bin, name)

    global_size = [8]
    local_size = None
    cl_bufs = [cl_buf2, cl_buf]

    cl_ev: cl.Event = cl_bin(
        cl_queue[device],
        global_size,
        local_size,
        *cl_bufs
    )
    cl_ev.wait()

    cl.enqueue_copy(cl_queue[device], x2, cl_buf2, is_blocking=True)

    print(x2)
