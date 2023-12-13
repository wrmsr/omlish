import ctypes
import functools
import subprocess
from typing import Tuple
from typing import TypeVar

import gpuctypes.hip as hip

from ..codegen.kernel import LinearizerOptions
from ..device import Compiled
from ..device import LRUAllocator
from ..device import MallocAllocator
from ..helpers import DEBUG
from ..helpers import compile_cuda_style
from ..helpers import diskcache
from ..helpers import encode_args_cuda_style
from ..helpers import from_mv
from ..helpers import getenv
from ..helpers import init_c_var
from ..helpers import time_execution_cuda_style
from ..renderer.cstyle import HIPRenderer

# The default HIP stream is used for everything.
MOCKHIP = getenv("MOCKHIP")  # for CI. don't run kernels, only check if they compile


def check(status):
    if status != 0:
        raise RuntimeError(
            f"HIP Error {status}, {ctypes.string_at(hip.hipGetErrorString(status)).decode()}"
        )


# TODO: remove these helpers, they increase complexity
def hip_time_execution(cb, enable=False):
    return time_execution_cuda_style(
        cb,
        hip.hipEvent_t,
        hip.hipEventCreate,
        hip.hipEventRecord,
        hip.hipEventSynchronize,
        hip.hipEventDestroy,
        hip.hipEventElapsedTime,
        enable=enable,
    )  # noqa: E501


@diskcache
def compile_hip(prg) -> bytes:
    return compile_cuda_style(
        prg,
        [f"--offload-arch={HIPDevice.default_arch_name}"],
        hip.hiprtcProgram,
        hip.hiprtcCreateProgram,
        hip.hiprtcCompileProgram,
        hip.hiprtcGetCode,
        hip.hiprtcGetCodeSize,
        hip.hiprtcGetProgramLog,
        hip.hiprtcGetProgramLogSize,
        check,
    )  # noqa: E501


class HIPProgram:
    def __init__(self, device: int, name: str, lib: bytes):
        self.device, self.name, self.lib = device, name, lib

        if DEBUG >= 6:
            asm = subprocess.check_output(
                ["/opt/rocm/llvm/bin/llvm-objdump", "-d", "-"], input=lib
            )
            print(
                "\n".join(
                    [
                        x
                        for x in asm.decode("utf-8").split("\n")
                        if "s_code_end" not in x
                    ]
                )
            )

        if MOCKHIP:
            return
        check(hip.hipSetDevice(self.device))
        self.module = init_c_var(
            hip.hipModule_t(),
            lambda x: check(hip.hipModuleLoadData(ctypes.byref(x), lib)),
        )
        self.prg = init_c_var(
            hip.hipFunction_t(),
            lambda x: check(
                hip.hipModuleGetFunction(
                    ctypes.byref(x), self.module, name.encode("utf-8")
                )
            ),
        )

    def __del__(self):
        if not MOCKHIP:
            check(hip.hipModuleUnload(self.module))

    def __call__(
        self,
        *args,
        global_size: Tuple[int, int, int],
        local_size: Tuple[int, int, int],
        vals: Tuple[int, ...] = (),
        wait=False,
    ):
        if MOCKHIP:
            return float("inf")
        check(hip.hipSetDevice(self.device))
        return hip_time_execution(
            lambda: check(
                hip.hipModuleLaunchKernel(
                    self.prg,
                    *global_size,
                    *local_size,
                    0,
                    None,
                    None,
                    encode_args_cuda_style(
                        args, vals, hip.hipDeviceptr_t, marks=(1, 2, 3)
                    )[0],
                )
            ),
            enable=wait,
        )  # noqa: E501


T = TypeVar("T")


class HIPAllocator(LRUAllocator):
    def __init__(self, device):
        self.device = device
        super().__init__()

    def _alloc(self, size: int):
        check(hip.hipSetDevice(self.device))
        return init_c_var(
            hip.hipDeviceptr_t(), lambda x: check(hip.hipMalloc(ctypes.byref(x), size))
        )

    def _free(self, opaque: T):
        check(hip.hipFree(opaque))

    def copyin(self, dest: T, src: memoryview):
        check(hip.hipSetDevice(self.device))
        # TODO: have to make sure src isn't freed to make this async
        check(hip.hipMemcpy(dest, from_mv(src), len(src), hip.hipMemcpyHostToDevice))

    def copyout(self, dest: memoryview, src: T):
        check(hip.hipSetDevice(self.device))
        check(hip.hipMemcpy(from_mv(dest), src, len(dest), hip.hipMemcpyDeviceToHost))

    def transfer(self, dest: T, src: T, sz: int):
        check(hip.hipSetDevice(self.device))
        # TODO: hipMemcpyAsync, but you have to track the "src" buffer to not free it
        check(hip.hipMemcpy(dest, src, sz, hip.hipMemcpyDeviceToDevice))


class HIPDevice(Compiled):
    default_arch_name = "gfx1100"

    def __init__(self, device: str = ""):
        self.device = int(device.split(":")[1]) if ":" in device else 0
        if self.device == 0 and not MOCKHIP:
            HIPDevice.default_arch_name = init_c_var(
                hip.hipDeviceProp_t(),
                lambda x: check(hip.hipGetDeviceProperties(x, self.device)),
            ).gcnArchName.decode()  # noqa: E501

        from ..features.graph.hip import HIPGraph

        super().__init__(
            MallocAllocator if MOCKHIP else HIPAllocator(self.device),
            LinearizerOptions(device="HIP"),
            HIPRenderer,
            compile_hip,
            functools.partial(HIPProgram, self.device),
            HIPGraph,
        )

    def synchronize(self):
        check(hip.hipSetDevice(self.device))
        check(hip.hipDeviceSynchronize())
