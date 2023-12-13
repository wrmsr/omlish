from __future__ import annotations

import ctypes
import functools
import os
import pathlib
import subprocess
import tempfile
from typing import Any
from typing import List
from typing import Optional
from typing import Tuple

import Metal
import libdispatch

from ..codegen.kernel import LinearizerOptions
from ..device import Compiled
from ..device import LRUAllocator
from ..helpers import DEBUG
from ..helpers import diskcache
from ..helpers import getenv
from ..helpers import prod
from ..helpers import unwrap2
from ..renderer.cstyle import MetalRenderer


@diskcache
def compile_metal(prg, use_xcode=bool(getenv("METAL_XCODE"))) -> bytes:
    assert (
        MetalDevice.compiler_device
    ), "metal device creation is required for metal compile"
    if use_xcode:
        # NOTE: if you run llvm-dis on "air" you can see the llvm bytecode
        air = subprocess.check_output(
            ["xcrun", "-sdk", "macosx", "metal", "-x", "metal", "-c", "-", "-o", "-"],
            input=prg.encode("utf-8"),
        )
        return subprocess.check_output(
            ["xcrun", "-sdk", "macosx", "metallib", "-", "-o", "-"], input=air
        )
    options = Metal.MTLCompileOptions.new()
    library = unwrap2(
        MetalDevice.compiler_device.newLibraryWithSource_options_error_(
            prg, options, None
        )
    )
    return library.libraryDataContents().bytes().tobytes()


class MetalProgram:
    def __init__(self, device: MetalDevice, name: str, lib: bytes):
        self.device, self.name, self.lib = device, name, lib
        if DEBUG >= 6:
            with tempfile.NamedTemporaryFile(delete=True) as shader:
                shader.write(lib)
                shader.flush()
                os.system(
                    f"cd {pathlib.Path(__file__).parents[2]}/disassemblers/applegpu && python3 compiler_explorer.py {shader.name}"
                )
        data = libdispatch.dispatch_data_create(lib, len(lib), None, None)
        self.library = unwrap2(self.device.device.newLibraryWithData_error_(data, None))
        self.fxn = self.library.newFunctionWithName_(name)
        self.pipeline_state = unwrap2(
            self.device.device.newComputePipelineStateWithFunction_error_(
                self.fxn, None
            )
        )

    def __call__(
        self,
        *bufs,
        global_size: Tuple[int, int, int],
        local_size: Tuple[int, int, int],
        vals: Tuple[int, ...] = (),
        wait=False,
    ):
        assert (
            prod(local_size) <= self.pipeline_state.maxTotalThreadsPerThreadgroup()
        ), f"local size {local_size} bigger than {self.pipeline_state.maxTotalThreadsPerThreadgroup()} with exec width {self.pipeline_state.threadExecutionWidth()} memory length {self.pipeline_state.staticThreadgroupMemoryLength()}"  # noqa: E501
        command_buffer = self.device.mtl_queue.commandBuffer()
        encoder = command_buffer.computeCommandEncoder()
        encoder.setComputePipelineState_(self.pipeline_state)
        for i, a in enumerate(bufs):
            encoder.setBuffer_offset_atIndex_(a, 0, i)
        for i, a in enumerate(vals, start=len(bufs)):
            encoder.setBytes_length_atIndex_(ctypes.c_int32(a), 4, i)
        encoder.dispatchThreadgroups_threadsPerThreadgroup_(
            Metal.MTLSize(*global_size), Metal.MTLSize(*local_size)
        )
        encoder.endEncoding()
        command_buffer.commit()
        if wait:
            command_buffer.waitUntilCompleted()
            return command_buffer.GPUEndTime() - command_buffer.GPUStartTime()
        self.device.mtl_buffers_in_flight.append(command_buffer)


class MetalAllocator(LRUAllocator):
    def __init__(self, device: MetalDevice):
        self.device: MetalDevice = device
        super().__init__()

    def _alloc(self, size: int) -> Any:
        ret = self.device.device.newBufferWithLength_options_(
            size, Metal.MTLResourceStorageModeShared
        )
        if ret is None:
            raise MemoryError(f"Metal OOM while allocating {size=}")
        return ret

    def transfer(self, dest: Any, src: Any, sz: int):
        command_buffer = self.device.mtl_queue.commandBuffer()
        encoder = command_buffer.blitCommandEncoder()
        encoder.copyFromBuffer_sourceOffset_toBuffer_destinationOffset_size_(
            src, 0, dest, 0, sz
        )
        encoder.endEncoding()
        command_buffer.commit()
        self.device.mtl_buffers_in_flight.append(command_buffer)

    def from_buffer(self, src: memoryview) -> Optional[Any]:
        ret = self.device.device.newBufferWithBytesNoCopy_length_options_deallocator_(
            src, len(src), Metal.MTLResourceStorageModeShared, None
        )
        if ret:
            self.device.mv_in_metal.append(src)
        return ret

    def _free(self, opaque: Any):
        opaque.release()

    def as_buffer(self, src: Any) -> memoryview:
        self.device.synchronize()
        return src.contents().as_buffer(src.length())

    def copyin(self, dest: Any, src: memoryview):
        self.as_buffer(dest)[:] = src

    def copyout(self, dest: memoryview, src: Any):
        dest[:] = self.as_buffer(src)


class MetalDevice(Compiled):
    compiler_device = None

    def __init__(self, device: str):
        self.device = Metal.MTLCreateSystemDefaultDevice()
        if MetalDevice.compiler_device is None:
            MetalDevice.compiler_device = self.device
        self.mtl_queue = self.device.newCommandQueueWithMaxCommandBufferCount_(1024)
        self.mtl_buffers_in_flight: List[Any] = []
        self.mv_in_metal: List[memoryview] = []
        from ..features.graph.metal import MetalGraph

        super().__init__(
            MetalAllocator(self),
            LinearizerOptions(device="METAL"),
            MetalRenderer,
            compile_metal,
            functools.partial(MetalProgram, self),
            functools.partial(MetalGraph, self),
        )

    def synchronize(self):
        for cbuf in self.mtl_buffers_in_flight:
            cbuf.waitUntilCompleted()
        self.mv_in_metal.clear()
        self.mtl_buffers_in_flight.clear()
