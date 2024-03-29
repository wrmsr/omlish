import subprocess
import time
import re
import hashlib
import tempfile
import pathlib
import typing as ta

from pycuda.compiler import compile as cuda_compile  # type: ignore
import numpy as np

from ..codegen.kernel import LinearizerOptions
from ..execution import Compiled
from ..helpers import DEBUG
from ..helpers import colored
from ..helpers import diskcache
from ..helpers import getenv
from ..renderer.cuda import CudaRenderer
from ..runtime.lib import LruAllocator
from ..runtime.lib import RawBufferCopyInOut
from ..runtime.lib import RawMallocBuffer


import os


os.environ['PATH'] = f"/usr/local/cuda-12.2/bin:{os.environ.get('PATH', '')}"
os.environ['CUDA_ROOT'] = '/usr/local/cuda-12.2/'


def pretty_ptx(s):
    # all expressions match `<valid_before><expr><valid_after>` and replace it with `<valid_before>color(<expr>)<valid_after>`
    s = re.sub(r'([!@<\[\s,\+\-;\n])((?:[_%$][\w%\$_]+(?:\.[xyz])?\:?)|(?:buf\d+))([<>\]\s,\+\-;\n\)])', lambda m: m[1] + colored(m[2], "blue") + m[3], s, flags=re.M)  # identifiers
    s = re.sub(r'(.)((?:b|s|u|f)(?:8|16|32|64)|pred)([\.\s])', lambda m: m[1] + colored(m[2], "green") + m[3], s, flags=re.M)  # types
    s = re.sub(r'^(\s*)([\w]+)(.*?;$)', lambda m: m[1] + colored(m[2], "yellow") + m[3], s, flags=re.M)  # instructions
    s = re.sub(r'([<>\[\]\s,\+\-;])((?:0[fF][0-9a-fA-F]{8})|(?:[0-9]+)|(?:0[xX][0-9a-fA-F]+))([<>\[\]\s,\+\-;])', lambda m: m[1] + colored(m[2], "yellow") + m[3], s, flags=re.M)  # numbers
    s = re.sub(r'(\.)(param|reg|global)', lambda m: m[1] + colored(m[2], "magenta"), s, flags=re.M)  # space
    s = re.sub(r'(\.)(version|target|address_size|visible|entry)', lambda m: m[1] + colored(m[2], "magenta"), s, flags=re.M)  # derivatives
    return s


def arch():
    return "sm_" + "".join([str(x) for x in pycuda.driver.Context.get_device().compute_capability()])


if getenv("CUDACPU", 0) == 1:
    import ctypes
    import ctypes.util

    lib = ctypes.CDLL(ctypes.util.find_library("gpuocelot"))
    lib.ptx_run.argtypes = [
        ctypes.c_char_p,
        ctypes.c_int,
        ctypes.POINTER(ctypes.c_void_p),
        ctypes.c_int,
        ctypes.c_int,
        ctypes.c_int,
        ctypes.c_int,
        ctypes.c_int,
        ctypes.c_int,
        ctypes.c_int,
    ]

    class cuda:
        class module:
            def __init__(self, src):
                self.src = src

            def get_function(self, _):
                return self

            def __call__(self, *args, block, grid, shared):
                lib.ptx_run(
                    self.src,
                    len(args),
                    (ctypes.c_void_p * len(args))(*[ctypes.cast(x, ctypes.c_void_p) for x in args]),
                    *block,
                    *grid,
                    shared,
                )

        module_from_buffer = lambda src: cuda.module(src)  # pylint: disable=unnecessary-lambda # noqa: E731

        class Event:
            def __init__(self):
                pass

            def record(self):
                self.start = time.perf_counter()

            def time_till(self, other):
                return other.start - self.start

            def synchronize(self):
                pass

        class Context:
            synchronize = lambda: 0  # noqa: E731

        CompileError = Exception


    class context:
        class device:
            compute_capability = lambda: (3, 5)  # pylint: disable=unnecessary-lambda # noqa: E731

        get_device = lambda: context.device  # pylint: disable=unnecessary-lambda # noqa: E731

    import pycuda.driver  # type: ignore

    pycuda.driver.Context = context
    RawCudaBuffer = RawMallocBuffer

else:
    import pycuda.autoprimaryctx  # type: ignore # pylint: disable=unused-import # noqa: F401
    import pycuda.driver as cuda  # type: ignore

    class CudaAllocator(LruAllocator):
        def __init__(self):
            super().__init__(self._get_cur_free_space(None))

        def _do_alloc(self, size, dtype, device, **kwargs):
            return cuda.mem_alloc(size * dtype.itemsize)  # type: ignore

        def _cached_bufkey(self, size, dtype, device):
            return (device, size * dtype.itemsize)  # Buffers of the same length could be reused, no matter what dtype.

        def _get_cur_free_space(self, device):
            return cuda.mem_get_info()[0]  # type: ignore

    CudaAlloc = CudaAllocator()  # type: ignore

    class RawCudaBuffer(RawBufferCopyInOut):  # type: ignore
        def __init__(self, size, dtype):
            super().__init__(size, dtype, allocator=CudaAlloc)

        def _copyin(self, x: np.ndarray, stream: ta.Optional[cuda.Stream] = None):
            cuda.memcpy_htod_async(self._buf, x.ravel(), stream)  # type: ignore

        def _copyout(self, x: np.ndarray):
            cuda.memcpy_dtoh(x, self._buf)  # type: ignore


@diskcache
def compile_cuda(prg: str) -> bytes:
    return cuda_compile(
        prg,
        target="ptx",
        no_extern_c=True,
        options=[
            '-Wno-deprecated-gpu-targets',
        ],
    )


class CudaProgram:
    def __init__(self, name: str, _prg: str) -> None:
        super().__init__()

        prg = _prg.decode('utf-8')

        if DEBUG >= 5:
            print(pretty_ptx(prg))

        if DEBUG >= 6:
            try:
                fn = (pathlib.Path(tempfile.gettempdir()) / f"tinycuda_{hashlib.md5(prg.encode('utf-8')).hexdigest()}").as_posix()
                with open(fn + ".ptx", "wb") as f:
                    f.write(prg.encode('utf-8'))
                subprocess.run(["ptxas", f"-arch={arch()}", "-o", fn, fn + ".ptx"], check=True)
                print(subprocess.check_output(['nvdisasm', fn]).decode('utf-8'))
            except Exception as e:
                print("failed to generate SASS", str(e))

        # TODO: name is wrong, so we get it from the ptx using hacks
        self.prg = cuda.module_from_buffer(prg.encode('utf-8')).get_function(prg.split(".visible .entry ")[1].split("(")[0])

    def __call__(
            self,
            *args,
            global_size: tuple[int, int, int],
            local_size: tuple[int, int, int],
            shared: int = 0,
            wait=False,
    ):
        if wait:
            start, end = cuda.Event(), cuda.Event()
            start.record()

        self.prg(
            *[
                x._buf if isinstance(x, RawCudaBuffer) else
                np.int32(x) if (isinstance(x, int) and not getenv("CUDACPU")) else
                x
                for x in args
            ],
            block=tuple(local_size),
            grid=tuple(global_size),
            shared=shared,
        )

        if wait:
            end.record()
            end.synchronize()
            return start.time_till(end) * 1e-3


if getenv("TRITON") == 1:
    from ..renderer.triton import uops_to_triton

    CudaBuffer = Compiled(
        RawCudaBuffer,
        LinearizerOptions(
            supports_float4=False,
            supports_float4_alu=False,
            global_max = [65535, 65535, 2147483647],
            local_max = [64, 1024, 1024],
            has_shared=False,
        ),
        uops_to_triton,
        lambda x: x.encode('utf-8'),
        CudaProgram,
        cuda.Context.synchronize,
    )

else:
    CudaBuffer = Compiled(
        RawCudaBuffer,
        LinearizerOptions(
            supports_float4=True,
            supports_float4_alu=False,
            global_max=[65535, 65535, 2147483647],
            local_max=[64, 1024, 1024],
        ),
        CudaRenderer,
        compile_cuda,
        CudaProgram,
        cuda.Context.synchronize,
    )
