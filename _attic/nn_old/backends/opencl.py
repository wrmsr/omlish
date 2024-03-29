import platform
import typing as ta

from omlish import defs
from omlish import lang

if ta.TYPE_CHECKING:
    import pyopencl as cl
else:
    cl = lang.proxy_import('pyopencl')

from .. import evaluators
from ..buffers import Buffer
from ..codegen.cstyle import CstyleCodegen
from ..codegen.cstyle import CstyleDialect
from ..devices import Device
from ..dtypes import Dtype
from ..evaluators import Evaluator
from ..codegen.codegen import Program
from ..numpy import NumpyValue
from ..raw import RawBufferCopyInOut
from ..raw import RawConst


_DEVICE_ATTR = '_omlish_device'


class OpenclRuntime:
    def __init__(self) -> None:
        super().__init__()

        dev_lsts: ta.List[ta.List[cl.Device]] = [
            ds
            for dt in (cl.device_type.GPU, cl.device_type.CPU)
            for ds in [plat.get_devices(device_type=dt) for plat in cl.get_platforms()]
            if ds
        ]

        self._context: cl.Context = cl.Context(devices=dev_lsts[0])

        self._queue: ta.List[cl.CommandQueue] = [
            cl.CommandQueue(
                self._context,
                device=dev,
                properties=cl.command_queue_properties.PROFILING_ENABLE,
            )
            for dev in self._context.devices
        ]

    @property
    def context(self) -> cl.Context:
        return self._context

    @property
    def queue(self) -> ta.List[cl.CommandQueue]:
        return self._queue


@lang.cached_nullary
def _runtime() -> OpenclRuntime:
    return OpenclRuntime()


class OpenclBuffer(RawBufferCopyInOut):

    def __init__(self, sz: int, dt: Dtype, device: int = 0) -> None:
        super().__init__(sz, dt)
        self._buf = cl.Buffer(_runtime().context, cl.mem_flags.READ_WRITE, sz * dt.item_size)
        setattr(self._buf, _DEVICE_ATTR, device)  # device is tracked on the underlying buffer

    def _copy_in(self, x: NumpyValue) -> None:
        cl.enqueue_copy(_runtime().queue[getattr(self._buf, _DEVICE_ATTR)], self._buf, x, is_blocking=False)

    def _copy_out(self, x: NumpyValue) -> None:
        cl.enqueue_copy(_runtime().queue[getattr(self._buf, _DEVICE_ATTR)], x, self._buf, is_blocking=True)


class OpenclCodegen(CstyleCodegen):
    pass


class OpenclCompiler(evaluators.Compiler):
    def __init__(self) -> None:
        super().__init__(
            OpenclBuffer,
            OpenclCodegen(),
        )


OpenclDialect = CstyleDialect(
    kernel_prefix='__kernel',
    buffer_prefix='__global ',
    smem_prefix='__local ',

    barrier='barrier(CLK_LOCAL_MEM_FENCE);',

    gid=[f'get_group_id({i})' for i in range(3)],
    lid=[f'get_local_id({i})' for i in range(3)],

    float4='(float4)',

    half_prekernel='#pragma OPENCL EXTENSION cl_khr_fp16 : enable',

    uses_vload=True,
)


@lang.cached_nullary
def opencl_compiler() -> evaluators.Compiler:
    return OpenclCompiler()


class OpenclDevice(Device):

    defs.repr()

    @property
    def evaluator(self) -> Evaluator:
        return opencl_compiler()

    def make_raw_buffer(self, obj: ta.Any) -> OpenclBuffer:
        return OpenclBuffer.from_cpu(obj)  # noqa


_IS_OSX = platform.system() == "Darwin"
_OSX_TIMING_RATIO = (
    (125 / 3) if _IS_OSX else 1.0
)  # see test/external_osx_profiling.py to determine this ratio. it's in like GPU clocks or something


class OpenclProgram(Program):
    def __init__(
            self,
            name: str,
            src: str,
            global_size: ta.Optional[ta.Sequence[int]] = None,
            local_size: ta.Optional[ta.Sequence[int]] = None,
    ) -> None:
        super().__init__()

        print(name)
        print(src)
        print()

        self._name = name
        self._src = src
        self._global_size = global_size
        self._local_size = local_size

        rt: OpenclRuntime = _runtime()
        self._cl_prg = cl.Program(rt.context, src)
        self._cl_bin = self._cl_prg.build()
        self._cl_fn = getattr(self._cl_bin, name)

    @property
    def name(self) -> str:
        return self._name

    def _cl_exec(self, global_size, local_size, *bufs, wait=False) -> ta.Optional[float]:
        cl_bufs = [x._buf if isinstance(x, OpenclBuffer) else x for x in bufs]

        rt: OpenclRuntime = _runtime()
        e = self._cl_fn(
            rt.queue[getattr(cl_bufs[0], _DEVICE_ATTR)],
            [g * l for g, l in zip(global_size, local_size)] if local_size is not None else global_size,
            local_size,
            *cl_bufs,
        )

        if wait:
            e.wait()
            try:
                return ((e.profile.end - e.profile.start) * _OSX_TIMING_RATIO) * 1e-9
            except cl.RuntimeError:  # no profiling info available
                return None

        return None

    def exec(self, bufs: ta.Sequence[Buffer]) -> None:
        raw_bufs = [
            x.get_realized()
            for x in bufs
            if x.is_realized and not isinstance(x.get_realized(), RawConst)
        ]

        self._cl_exec(
            ([*self._global_size, *([1] * (3 - len(self._global_size)))]) if self._global_size is not None else None,
            ([*self._local_size, *([1] * (3 - len(self._local_size)))]) if self._local_size is not None else None,
            *raw_bufs,
            wait=True,
        )
