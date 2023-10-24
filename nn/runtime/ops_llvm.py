import time
import hashlib
import ctypes
import typing as ta
import ctypes as ct

import llvmlite.binding as llvm

from ..codegen.kernel import LinearizerOptions
from ..execution import Compiled
from ..helpers import DEBUG
from ..helpers import getenv
from ..renderer.llvmir import uops_to_llvm_ir
from ..runtime.lib import RawMallocBuffer


class LLVM:
    target_machine: ta.ClassVar[llvm.targets.TargetMachine] = None
    engine: ta.ClassVar[llvm.executionengine.ExecutionEngine] = None
    optimizer: ta.ClassVar[llvm.passmanagers.ModulePassManager] = None

    def __init__(self) -> None:
        super().__init__()
        if LLVM.engine is not None:
            return
        llvm.initialize()
        llvm.initialize_native_target()
        llvm.initialize_native_asmprinter()
        llvm.initialize_native_asmparser()
        target = llvm.Target.from_triple(llvm.get_process_triple())
        LLVM.optimizer = llvm.create_module_pass_manager()
        LLVM.target_machine = target.create_target_machine(
            opt=2
        )  # this opt actually can change things. ex: opt=3 means no FMA, opt=2 means FMA
        LLVM.target_machine.add_analysis_passes(LLVM.optimizer)

        # TODO: this makes compile times so much faster
        if getenv("LLVMOPT"):
            llvm.set_option(
                str(), "-force-vector-interleave=4"
            )  # this makes sum the same speed as torch, it also doubles the (slow) conv speed
            if DEBUG >= 4:
                llvm.set_option(str(), "--debug-only=loop-vectorize")
            # llvm.set_option(str(), '--debug')

            # does this do anything?
            builder = llvm.create_pass_manager_builder()
            builder.opt_level = 3
            builder.size_level = 0
            builder.loop_vectorize = True
            builder.slp_vectorize = True
            builder.populate(LLVM.optimizer)

        LLVM.target_machine.set_asm_verbosity(True)
        backing_mod = llvm.parse_assembly(str())
        backing_mod.triple = llvm.get_process_triple()
        LLVM.engine = llvm.create_mcjit_compiler(backing_mod, LLVM.target_machine)


class LlvmProgram:
    def __init__(self, name: str, prg: str, binary=False) -> None:
        super().__init__()
        print(prg)
        print()
        self.mod = llvm.parse_assembly(prg)
        self.mod.verify()
        LLVM().optimizer.run(self.mod)
        self.mod.name = hashlib.sha1(prg.encode("utf-8")).hexdigest()
        if DEBUG >= 5:
            print(LLVM.target_machine.emit_assembly(self.mod))
        LLVM.engine.add_module(self.mod)
        LLVM.engine.finalize_object()
        self.fxn = LLVM.engine.get_function_address(name)

    def __del__(self):
        if hasattr(self, "mod"):
            LLVM.engine.remove_module(self.mod)

    def __call__(self, unused_global_size, unused_local_size, *bufs, wait=False):
        cfunc = ct.CFUNCTYPE(ctypes.c_int, *[ctypes.c_void_p for _ in bufs])(self.fxn)
        if wait:
            st = time.monotonic()
        cfunc(*[x._buf if not isinstance(x, int) else x for x in bufs])
        if wait:
            return time.monotonic() - st


LlvmBuffer = Compiled(
    RawMallocBuffer,
    LinearizerOptions(
        supports_float4=False,
        has_local=False,
        has_shared=False,
    ),
    uops_to_llvm_ir,
    LlvmProgram,
)
