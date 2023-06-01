import typing as ta

from omlish import lang

if ta.TYPE_CHECKING:
    import pyopencl as cl
else:
    cl = lang.proxy_import('pyopencl')

from . import evaluators
from .devices import Device
from .dtypes import Dtype
from .evaluators import Evaluator
from .numpy import NumpyValue
from .raw import RawBufferCopyInOut


class OpenclDevice(Device):
    @property
    def evaluator(self) -> Evaluator:
        raise NotImplementedError


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

    def context(self) -> cl.Context:
        return self._context

    def queue(self) -> ta.List[cl.CommandQueue]:
        return self._queue


@lang.cached_nullary
def _runtime() -> OpenclRuntime:
    return OpenclRuntime()


class OpenclBuffer(RawBufferCopyInOut):
    def __init__(self, sz: int, dt: Dtype, device: int = 0) -> None:
        buf = cl.Buffer(_runtime().context, cl.mem_flags.READ_WRITE, sz * dt.item_size)
        setattr(buf, "device", device)  # device is tracked on the underlying buffer
        super().__init__(sz, dt, buf)

    def _copy_in(self, x: np.ndarray):
        assert not self.dtype.name.startswith(
            "image"
        ), f"can't copyin images {self.dtype}"
        cl.enqueue_copy(_runtime().queue[self._buf.device], self._buf, x, is_blocking=False)

    def _copy_out(self, x: np.ndarray):
        assert not self.dtype.name.startswith(
            "image"
        ), f"can't copyout images {self.dtype}"
        cl.enqueue_copy(CL.cl_queue[self._buf.device], x, self._buf, is_blocking=True)



# class OpenclCompiler(evaluators.Compiler):
#     def __int__(self) -> None:
#         super().__init__(
#
#         )


@lang.cached_nullary
def opencl_compiler() -> evaluators.Compiler:
    raise NotImplementedError
