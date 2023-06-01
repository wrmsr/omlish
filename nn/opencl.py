import typing as ta

from omlish import lang

if ta.TYPE_CHECKING:
    import pyopencl as cl
else:
    cl = lang.proxy_import('pyopencl')

from . import evaluators
from .codegen import CstyleCodegen
from .devices import Device
from .dtypes import Dtype
from .evaluators import Evaluator
from .numpy import NumpyValue
from .raw import RawBufferCopyInOut


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
        cl.enqueue_copy(_runtime().queue[self._buf.device], self._buf, x, is_blocking=False)

    def _copy_out(self, x: NumpyValue) -> None:
        cl.enqueue_copy(_runtime().queue[self._buf.device], x, self._buf, is_blocking=True)


class OpenclCodegen(CstyleCodegen):
    pass


class OpenclCompiler(evaluators.Compiler):
    def __init__(self) -> None:
        super().__init__(
            OpenclBuffer,
            OpenclCodegen(),
        )


@lang.cached_nullary
def opencl_compiler() -> evaluators.Compiler:
    return OpenclCompiler()


class OpenclDevice(Device):
    @property
    def evaluator(self) -> Evaluator:
        return opencl_compiler()
