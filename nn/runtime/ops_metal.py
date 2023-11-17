import os
import subprocess
import pathlib
import ctypes
import tempfile
import typing as ta

from omlish import collections as col
import Cocoa  # noqa
import Metal  # noqa
import libdispatch  # noqa

from ..codegen.kernel import LinearizerOptions
from ..dtypes import DType
from ..dtypes import dtypes
from ..execution import Compiled
from ..execution import CompiledAstRunner
from ..execution import update_stats
from ..helpers import DEBUG
from ..helpers import diskcache
from ..helpers import getenv
from ..helpers import prod
from ..jit import BatchExecutor
from ..jit import JitItem
from ..renderer.metal import MetalRenderer
from ..runtime.lib import LruAllocator
from ..runtime.lib import RawBuffer
from ..runtime.lib import RawBufferMapped
from ..shape.symbolic import Node
from ..shape.symbolic import Variable


class MetalAllocator(LruAllocator):
    def _do_alloc(self, size, dtype, device, **kwargs):
        buf_len, max_buf_len = size * dtype.itemsize, METAL.device.maxBufferLength()
        assert (
            buf_len < max_buf_len
        ), f"Buffer length of {buf_len / 1e9:5.2f} GB exceeds Metal's max buffer length of {max_buf_len / 1e9:5.2f} GB."
        buf = METAL.device.newBufferWithLength_options_(buf_len, Metal.MTLResourceStorageModeShared)
        assert buf, f"Metal buffer allocation failed with {buf}."
        return buf

    def _do_free(self, buf):
        buf.release()

    def _cached_bufkey(self, size, dtype, device):
        return (
            device,
            size * dtype.itemsize,
        )  # Buffers of the same length could be reused, no matter what dtype.


class _METAL:
    def __init__(self) -> None:
        super().__init__()
        self.mtl_buffers_in_flight: list[ta.Any] = []
        self.device = Metal.MTLCreateSystemDefaultDevice()
        self.supports_icb = (
            (
                self.device.supportsFamily_(Metal.MTLGPUFamilyMac2)
                or self.device.supportsFamily_(Metal.MTLGPUFamilyApple3)
                or self.device.supportsFamily_(Metal.MTLGPUFamilyCommon2)
            )
            and self.device.argumentBuffersSupport() is Metal.MTLArgumentBuffersTier2
        )
        self.mtl_queue = self.device.newCommandQueueWithMaxCommandBufferCount_(1024)
        self.allocator = MetalAllocator(
            self.device.dedicatedMemorySize() or self.device.sharedMemorySize()
        )

    # TODO: is there a better way to do this?
    def synchronize(self):
        for cbuf in self.mtl_buffers_in_flight:
            cbuf.waitUntilCompleted()
        self.mtl_buffers_in_flight.clear()


METAL = _METAL()


class RawMetalBuffer(RawBufferMapped):
    def __init__(self, size: int, dtype: DType) -> None:
        assert dtype != dtypes.double, f"METAL does not support {dtype.name}"
        super().__init__(size, dtype, allocator=METAL.allocator)

    def _buffer(self):
        METAL.synchronize()
        return self._buf.contents().as_buffer(self._buf.length())


def unwrap(x):
    ret, err = x
    assert err is None, str(err)
    return ret


@diskcache
def compile_metal(prg: str, use_xcode: bool = bool(getenv("METAL_XCODE"))) -> bytes:
    if use_xcode:
        # NOTE: if you run llvm-dis on "air" you can see the llvm bytecode
        air = subprocess.check_output(
            [
                'xcrun',
                '-sdk', 'macosx',
                'metal',
                '-x', 'metal',
                '-c', '-',
                '-o', '-',
            ],
            input=prg.encode('utf-8'),
        )
        return subprocess.check_output(
            [
                'xcrun',
                '-sdk', 'macosx',
                'metallib',
                '-',
                '-o', '-',
            ],
            input=air,
        )

    options = Metal.MTLCompileOptions.new()
    library = unwrap(METAL.device.newLibraryWithSource_options_error_(prg, options, None))

    # TODO: avoid file write here?
    with tempfile.NamedTemporaryFile(delete=True) as output_file:
        unwrap(library.serializeToURL_error_(Cocoa.NSURL.URLWithString_(f"file://{output_file.name}"), None))
        return pathlib.Path(output_file.name).read_bytes()


class MetalProgram:
    def __init__(self, name: str, lib: bytes) -> None:
        super().__init__()
        data = libdispatch.dispatch_data_create(lib, len(lib), None, None)
        self.library = unwrap(METAL.device.newLibraryWithData_error_(data, None))
        self.fxn = self.library.newFunctionWithName_(name)
        if DEBUG >= 6:
            with tempfile.NamedTemporaryFile(delete=True) as shader:
                shader.write(lib)
                shader.flush()
                os.system(
                    f"cd {pathlib.Path(__file__).parents[2]}/disassemblers/applegpu && "
                    f"python3 compiler_explorer.py {shader.name}"
                )
        self.pipeline_state = unwrap(METAL.device.newComputePipelineStateWithFunction_error_(self.fxn, None))

    def __call__(
            self,
            *bufs,
            global_size: tuple[int, int, int],
            local_size: tuple[int, int, int],
            wait=False,
    ):
        assert (
            prod(local_size) <= self.pipeline_state.maxTotalThreadsPerThreadgroup()
        ), (
            f"local size {local_size} bigger than {self.pipeline_state.maxTotalThreadsPerThreadgroup()} "
            f"with exec width {self.pipeline_state.threadExecutionWidth()} "
            f"memory length {self.pipeline_state.staticThreadgroupMemoryLength()}"
        )

        command_buffer = METAL.mtl_queue.commandBuffer()

        encoder = command_buffer.computeCommandEncoder()
        encoder.setComputePipelineState_(self.pipeline_state)
        for i, a in enumerate(bufs):
            if isinstance(a, RawMetalBuffer):
                encoder.setBuffer_offset_atIndex_(a._buf, 0, i)
            elif isinstance(a, int):
                encoder.setBytes_length_atIndex_(
                    (arg := ctypes.c_int32(a)), ctypes.sizeof(arg), i
                )
            else:
                raise RuntimeError(f"arg at index {i} has unsupported type {type(a)}")
        encoder.dispatchThreadgroups_threadsPerThreadgroup_(Metal.MTLSize(*global_size), Metal.MTLSize(*local_size))
        encoder.endEncoding()

        command_buffer.commit()

        if wait:
            command_buffer.waitUntilCompleted()
            return command_buffer.GPUEndTime() - command_buffer.GPUStartTime()

        METAL.mtl_buffers_in_flight.append(command_buffer)


class MetalBatchExecutor(BatchExecutor):
    def __init__(
            self,
            jit_cache: list[JitItem],
            input_rawbuffers: dict[ta.Union[int, str], RawBuffer],
            var_vals: dict[Variable, int],
    ) -> None:
        super().__init__(jit_cache, input_rawbuffers, var_vals)

        # create metal batch exec
        icb_descriptor = Metal.MTLIndirectCommandBufferDescriptor.new()
        icb_descriptor.setCommandTypes_(Metal.MTLIndirectCommandType(Metal.MTLIndirectCommandTypeConcurrentDispatch))
        icb_descriptor.setInheritBuffers_(False)
        icb_descriptor.setInheritPipelineState_(False)
        icb_descriptor.setMaxKernelBufferBindCount_(31)

        self.icb = METAL.device.newIndirectCommandBufferWithDescriptor_maxCommandCount_options_(
            icb_descriptor,
            len(self.jit_cache),
            Metal.MTLResourceOptions(0),
        )
        assert self.icb is not None, "create indirect command buffer failed, does your system support this?"

        self.int_buf = RawMetalBuffer(len(var_vals), dtypes.int32)
        self.input_has_variable_dims: set[int] = set()

        read_resources, write_resources = [], []
        for j, ji in enumerate(self.jit_cache):
            prg: CompiledAstRunner = ta.cast(CompiledAstRunner, ji.prg)
            descriptor = Metal.MTLComputePipelineDescriptor.new()
            descriptor.setComputeFunction_(prg.clprg.fxn)
            descriptor.setSupportIndirectCommandBuffers_(True)

            pipeline_state = unwrap(METAL.device.newComputePipelineStateWithDescriptor_options_reflection_error_(
                descriptor,
                Metal.MTLPipelineOption(0),
                None,
                None,
            ))

            icb_command = self.icb.indirectComputeCommandAtIndex_(j)
            icb_command.setComputePipelineState_(pipeline_state)
            for i, b in enumerate(ji.rawbufs):
                if b is not None:
                    icb_command.setKernelBuffer_offset_atIndex_(b._buf, 0, i)
                    if i == 0:
                        write_resources.append(b._buf)
                    else:
                        read_resources.append(b._buf)

            var_vals_keys = list(var_vals.keys())
            for i, v in enumerate(prg.vars):
                icb_command.setKernelBuffer_offset_atIndex_(
                    self.int_buf._buf,
                    var_vals_keys.index(v) * 4,
                    len(ji.rawbufs) + i,
                )

            global_size, local_size = prg.launch_dims(var_vals)
            assert prg.global_size and prg.local_size, "need global and local size to JIT"
            if (
                    any(isinstance(x, Node) for x in prg.global_size)
                    or any(isinstance(x, Node) for x in prg.local_size)
            ):
                self.input_has_variable_dims.add(j)
            else:
                icb_command.concurrentDispatchThreadgroups_threadsPerThreadgroup_(
                    Metal.MTLSize(*global_size),
                    Metal.MTLSize(*local_size),
                )
            icb_command.setBarrier()

        self.read_resources = col.unique(read_resources)
        self.write_resources = col.unique(write_resources)
        self.command_buffer: ta.Any = None
        self.int_buf_view = self.int_buf.buffer_view()  # TODO: this is metal syncing when it doesn't need to

    def __call__(
            self,
            input_rawbuffers: dict[ta.Union[int, str], RawBuffer],
            var_vals: dict[Variable, int],
            wait=False,
    ):
        # NOTE: you at least can't update the ints if this is running
        if self.command_buffer is not None and self.command_buffer in METAL.mtl_buffers_in_flight:
            self.command_buffer.waitUntilCompleted()

        all_read_resources = self.read_resources + [x._buf for x in input_rawbuffers.values()]

        for (j, i), input_name in self.input_replace.items():
            self.icb.\
                indirectComputeCommandAtIndex_(j).\
                setKernelBuffer_offset_atIndex_(input_rawbuffers[input_name]._buf, 0, i)

        for j in self.input_has_variable_dims:
            global_size, local_size = ta.cast(CompiledAstRunner, self.jit_cache[j].prg).launch_dims(var_vals)
            self.icb.\
                indirectComputeCommandAtIndex_(j).\
                concurrentDispatchThreadgroups_threadsPerThreadgroup_(Metal.MTLSize(*global_size), Metal.MTLSize(*local_size))  # noqa

        self.int_buf_view[:] = list(var_vals.values())

        command_buffer = METAL.mtl_queue.commandBuffer()

        encoder = command_buffer.computeCommandEncoder()
        encoder.executeCommandsInBuffer_withRange_(self.icb, Metal.MTLIndirectCommandBufferExecutionRangeMake(0, len(self.jit_cache)))
        encoder.useResources_count_usage_(all_read_resources, len(all_read_resources), Metal.MTLResourceUsageRead)
        encoder.useResources_count_usage_(self.write_resources, len(self.write_resources), Metal.MTLResourceUsageWrite)
        encoder.endEncoding()

        command_buffer.commit()

        self.command_buffer = command_buffer

        if wait:
            command_buffer.waitUntilCompleted()
            et = command_buffer.GPUEndTime() - command_buffer.GPUStartTime()
        else:
            METAL.mtl_buffers_in_flight.append(command_buffer)
            et = None

        update_stats(
            f"<batched {len(self.jit_cache)}>",
            self.op_estimate,
            self.mem_estimate,
            var_vals,
            et,
            buf_count=len(input_rawbuffers),
            jit=True,
            num_kernels=len(self.jit_cache),
        )

        return et


MetalBuffer = Compiled(
    RawMetalBuffer,
    LinearizerOptions(device="METAL"),
    MetalRenderer,
    compile_metal,
    MetalProgram,
    METAL.synchronize,
    batch_executor=MetalBatchExecutor if not METAL.supports_icb else BatchExecutor,
)
