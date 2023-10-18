from __future__ import annotations

import itertools
import random
import time
import typing as ta

from omlish import dataclasses as dc
import numpy as np

from . import ops
from .dtypes import DType
from .helpers import BEAM
from .helpers import DEBUG
from .helpers import GlobalCounters
from .helpers import ansilen
from .helpers import colored
from .helpers import getenv
from .helpers import prod
from .ops import LazyOp
from .runtime.lib import RawBuffer
from .shape.symbolic import Variable
from .shape.symbolic import sym_infer

if ta.TYPE_CHECKING:
    from .lazy import LazyBuffer
    from .shape.shapetracker import ShapeTracker


@dc.dataclass(frozen=True)
class MemBuffer:
    idx: int
    dtype: DType
    st: ShapeTracker


@dc.dataclass(frozen=True)
class ConstBuffer:
    val: ta.Any
    dtype: DType
    st: ShapeTracker


@dc.dataclass(frozen=True)
class ScheduleItem:
    ast: LazyOp
    out: LazyBuffer
    inputs: tuple[LazyBuffer, ...]
    var_vals: dict[Variable, int]


# **************** for Interpreted Buffers ****************


class Interpreted:
    def __init__(
            self,
            buffer,
            fxn_for_op: dict[type[LazyOp], ta.Callable],
            to_underlying=lambda x: x._buf,
            from_underlying=None,
    ) -> None:
        super().__init__()
        self.buffer = buffer
        self.fxn_for_op = fxn_for_op
        self.to_underlying = to_underlying
        self.from_underlying = buffer if from_underlying is None else from_underlying
        self.synchronize = lambda: None
        self.codegen = None

    def exec_ast(
            self,
            ast: LazyOp,
            output=None,
            inputs=None,
            var_vals=None,
            context=None,
            **kwargs,
    ):
        if isinstance(ast, ops.BufferOp) and type(ast) not in self.fxn_for_op:
            if isinstance(ast, ops.Mem):
                assert inputs[ast.arg.idx - 1].dtype == ast.arg.dtype, "dtype mismatch"
                buf = self.to_underlying(inputs[ast.arg.idx - 1].realized)
            elif isinstance(ast, ops.Const):
                buf = self.to_underlying(self.buffer.fromCpu(np.array(ast.arg.val, dtype=ast.arg.dtype.np)))
            for mop, arg in ast.arg.st.to_movement_ops():
                buf = self.fxn_for_op[mop](buf, arg)
            return self.from_underlying(buf)

        if (
                ops.MulAcc in self.fxn_for_op
                and isinstance(ast, ops.Sum)
                and isinstance(ast.src[0], LazyOp)
                and isinstance(ast.src[0], ops.Mul)
        ):
            ast = ops.MulAcc(ast.src[0].src, ast.arg)

        created_context = context is None

        if context is None:
            context = dict()

        if not created_context and ast in context:
            return context[ast]

        srcs = [
            self.exec_ast(ta.cast(LazyOp, x), inputs=inputs, context=context, **kwargs)
            for x in ast.src
        ]

        if DEBUG >= 3:
            st = time.perf_counter()

        ret = self.from_underlying(
            self.fxn_for_op[type(ast)](
                *(
                    [self.to_underlying(x) for x in srcs] +
                    ([ast.arg] if ast.arg is not None else [])
                )
            )
        )

        if (
                output is not None
                and ret.dtype != output.dtype
                and ops.Cast in self.fxn_for_op
        ):
            ret = self.from_underlying(
                self.fxn_for_op[ops.Cast](
                    self.to_underlying(ret), (output.dtype, False)
                )
            )  # Do manual casting of ret if it does not match the required output dtype.

        if DEBUG >= 5 or (self.buffer != FlopCounter and DEBUG >= 3):
            print(
                (
                    f"*** {'exec' if created_context else '    '} "
                    f"{GlobalCounters.mem_used/1e9:5.2f} GB "
                    f"{(time.perf_counter()-st)*1e3:7.2f} ms "
                    f"op: {type(ast):20s} "
                    f"out({ret.dtype.name}): "
                    f"{str(ret._buf.shape) if hasattr(ret._buf, 'shape') else str(len(ret._buf)):30s} "
                    f"in({len(srcs)}):"
                ),
                list(
                    set(
                        x._buf.shape if hasattr(x._buf, "shape") else len(x._buf)
                        for x in srcs
                    )
                ),
                ast.arg if ast.arg is not None else "",
            )

        if not created_context:
            context[ast] = ret

        if output is not None and output.output_buffer is not None:
            # TODO: does this check have any meaning anymore?
            # It fails on things like batchnorm initted with zeros
            # assert output.output_buffer.size == ret.size, f"size mismatch, {output.output_buffer.size} != {ret.size}"
            assert output.output_buffer.dtype == ret.dtype
            output.output_buffer._buf = ret._buf
            return output.output_buffer

        return ret


# --teenygrad--


class FlopCounter:
    def __init__(self, tup: tuple[tuple[int, ...], DType, int]) -> None:
        super().__init__()
        self.shape, self.dtype, self.flops = tup
        self._buf = self

    def consume_flops(self):
        self.flops, ret = 0, self.flops
        return ret


shape_fxn_for_op: dict[type[LazyOp], ta.Callable] = {
    ops.Mem: lambda arg: (arg.st.shape, arg.dtype, 0),
    ops.Const: lambda arg: (arg.st.shape, arg.dtype, 0),
    ops.Cast: lambda self, arg: (
        self.shape,
        arg[0],
        self.consume_flops(),
    ),  # cast uses no flops
    **{
        op: lambda self: (
            self.shape,
            self.dtype,
            self.consume_flops() + prod(self.shape),
        )
        for op in ops.UnaryOp.__subclasses__()
        if op != ops.Cast
    },
    **{
        op: lambda self, y: (
            self.shape,
            max(self.dtype, y.dtype),
            self.consume_flops() + y.consume_flops() + prod(self.shape),
        )
        for op in ops.BinaryOp.__subclasses__()
    },
    **{
        op: lambda self, new_shape: (
            new_shape,
            self.dtype,
            self.consume_flops() + prod(self.shape),
        )
        for op in ops.ReduceOp.__subclasses__()
    },
    ops.Where: lambda self, y, z: (
        self.shape,
        y.dtype,
        self.consume_flops() + y.consume_flops() + z.consume_flops() + prod(self.shape),
    ),
}

InterpretedFlopCounter = Interpreted(FlopCounter, shape_fxn_for_op, lambda x: x)


def get_lazyop_info(ast: LazyOp) -> FlopCounter:
    return InterpretedFlopCounter.exec_ast(ast)


# **************** for Compiled Buffers ****************


class BasicBatchExecutor:
    def __init__(self, jit_cache: list[tuple[ta.Any, ta.Any, ta.Any]]) -> None:
        super().__init__()

    def exec(self, jit_cache: list[tuple[ta.Any, ta.Any, ta.Any]], updatable_entries):
        for prg, pargs, variables in jit_cache:
            prg(pargs, variables, jit=True)

    def recalc_stat(self, jit_cache: list[tuple[ta.Any, ta.Any, ta.Any]]) -> None:
        for prg, _, variables in jit_cache:
            GlobalCounters.kernel_count += 1
            GlobalCounters.global_ops += sym_infer(prg.op_estimate, variables)
            GlobalCounters.global_mem += prg.mem_estimate


class ASTRunner:
    def __init__(
            self,
            name,
            prg,
            global_size: ta.Optional[list[int]] = None,
            local_size: ta.Optional[list[int]] = None,
            op_estimate=0,
            mem_estimate=0,
            display_name: ta.Optional[str] = None,
            runtime_args: ta.Optional[dict] = None,
    ) -> None:
        super().__init__()
        if DEBUG >= 4 and (
                runtime_args is None
                or "binary" not in runtime_args
                or not runtime_args["binary"]
        ):
            print(prg)
        self.name = name
        self.prg = prg
        self.global_size = global_size
        self.local_size = local_size
        self.op_estimate = op_estimate
        self.mem_estimate = mem_estimate
        self.display_name = display_name
        self.runtime_args = runtime_args if runtime_args is not None else {}

    @staticmethod
    def from_linearizer(k, src: str):
        return ASTRunner(
            k.function_name,
            src,
            k.global_size, k.local_size,
            op_estimate=k.info.flops,
            mem_estimate=k.mem_estimate,
            display_name=k.display_name,
            runtime_args={"binary": False},
        )

    def optimize_local_size(self, global_size, rawbufs) -> List[int]:
        assert self.global_size is not None, "needs a global size to optimize local size"
        MAX_WORKGROUP = self.clprg.max_work_group_size() if hasattr(self.clprg, 'max_work_group_size') else 1024
        local_dims = [[x for x in set([sz, 1, 2, 4, 8, 16, 32, 64, 128, 256, MAX_WORKGROUP]) if x <= sz] for sz in global_size]
        local_sizes = [list(x) for x in itertools.product(*local_dims) if prod(x) <= MAX_WORKGROUP] * 2  # try each valid size twice

        def try_exec(local_size):
            try:
                return self.clprg([g // l if g % l == 0 else g / l for g, l in zip(global_size, local_size)], local_size, *rawbufs, wait=True)
            except Exception:
                return float('inf')

        return min([(try_exec(local_size), local_size) for local_size in random.sample(local_sizes, len(local_sizes))])[1]

    def build(self, runtime, batch_exec=BasicBatchExecutor):
        self.clprg, self.batch_exec = (runtime(self.name, self.prg, **self.runtime_args), batch_exec,)
        return self

    def exec(
            self,
            rawbufs,
            var_vals: ta.Optional[dict[Variable, int]] = None,
            force_wait=False,
            optimizing=False,
    ) -> ta.Optional[float]:
        from .jit import CacheCollector

        if not optimizing:
            CacheCollector.add(self, rawbufs, var_vals if var_vals is not None else {})

        return self(rawbufs, var_vals, force_wait=force_wait)

    def launch_dims(self, var_vals):
        global_size = (
            (
                [sym_infer(sz, var_vals) for sz in self.global_size]
                + [1] * (3 - len(self.global_size))
            )
            if self.global_size is not None
            else self.global_size
        )

        local_size = (
            (
                [sym_infer(sz, var_vals) for sz in self.local_size] +
                [1] * (3 - len(self.local_size))
            )
            if self.local_size is not None
            else self.local_size
        )

        return global_size, local_size

    def __call__(
            self,
            rawbufs: list[RawBuffer],
            var_vals: ta.Optional[dict[Variable, int]] = None,
            jit=False,
            force_wait=False,
    ) -> ta.Optional[float]:
        if var_vals is None:
            var_vals = {}

        global_size, local_size = self.launch_dims(var_vals)

        if global_size is not None and local_size is None:
            local_size = self.local_size = self.optimize_local_size(global_size, rawbufs)
            global_size = self.global_size = [g // l if g % l == 0 else g / l for g, l in zip(global_size, local_size)]

        if et := self.clprg(
                global_size,
                local_size,
                *rawbufs,
                *var_vals.values(),
                wait=force_wait or DEBUG >= 2,
        ):
            GlobalCounters.time_sum_s += et

        op_estimate = sym_infer(self.op_estimate, var_vals)

        if DEBUG >= 2:
            print(
                (
                    f"{colored(f'*** {GlobalCounters.kernel_count:4d}', 'magenta' if jit else None)} "
                    f"{(self.display_name+' '*(37-ansilen(self.display_name))) if self.display_name is not None else self.name:33s} "  # noqa
                    f"arg {len(rawbufs):3d} "
                    f"sz {str(global_size):18s} {str(local_size):12s} "
                    f"OPs {int(op_estimate/1e6):6d}M/{GlobalCounters.global_ops/1e9:7.2f}G  "
                    f"mem {GlobalCounters.mem_used/1e9:5.2f} GB "
                )
                + (
                    str()
                    if et is None
                    else (
                        f"tm "
                        f"{et*1e6:9.2f}us/{GlobalCounters.time_sum_s*1e3:9.2f}ms "
                        f"({op_estimate/((et or 1e-20)*1e9):8.2f} GFLOPS, "
                        f"{self.mem_estimate/((et or 1e-20)*1e9):7.2f} GB/s)"
                    )
                )
            )

        GlobalCounters.kernel_count += 1
        GlobalCounters.global_ops += op_estimate
        GlobalCounters.global_mem += self.mem_estimate

        return et


class Compiled:
    def __init__(
            self,
            buffer: type[RawBuffer],
            linearizer_opts,
            renderer,
            runtime,
            synchronize=lambda: None,
            batch_exec=BasicBatchExecutor,
    ) -> None:
        super().__init__()
        self.buffer = buffer
        self.linearizer_opts = linearizer_opts
        self.renderer = renderer
        self.runtime = runtime
        self.synchronize = synchronize
        self.batch_exec = batch_exec
        self.method_cache: dict[LazyOp, ASTRunner] = {}

    def to_program(self, k):
        k.linearize()

        src, runtime_args = self.renderer(k.function_name, k.uops)
        return ASTRunner(
            k.function_name,
            src,
            k.global_size,
            k.local_size,
            op_estimate=k.info.flops,
            mem_estimate=k.mem_estimate,
            display_name=k.display_name,
            runtime_args=runtime_args
        ).build(
            self.runtime,
            self.batch_exec,
        )

    def exec_ast(self, ast: LazyOp, output, inputs, var_vals, **kwargs):
        # if DEBUG >= 4:
        #  from .helpers import print_tree
        #  print_tree(ast)

        # check if we can reuse the output buffer
        # if it's aliased, don't use it
        # NOTE: this is pretty wrong actually, who knows where else this buffer is used?
        output.realized = output.output_buffer
        if output.realized:
            for i, a in enumerate(inputs):
                # TODO: if this is contiguous it's fine
                if a.realized == output.realized:
                    if any(
                            not x.arg.st.contiguous
                            for x in ast.get_lazyops()
                            if isinstance(x, ops.Mem) and x.arg.idx == i + 1
                    ):
                        output.realized = None
                        break

        # we don't have an output buffer, we have to create it, and create to max size if it has symbolic shape
        if not output.realized:
            output.realized = self.buffer(
                prod((s if isinstance(s, int) else s.max for s in output.shape)),
                output.dtype,
                **kwargs,
            )
        else:
            from .jit import CacheCollector

            CacheCollector._mark_output_buffer(output.output_buffer)

        # all the rawbuffers
        rawbuffers = [output.realized] + [x.realized for x in inputs]

        # extract real vars used in ast
        from .lazy import vars_from_ast
        ast_vars = vars_from_ast(ast)
        assert all(v.val is None for v in ast_vars), f"ast contains bound Variable {ast_vars}"

        # compilation time
        def get_program():
            from .codegen.linearizer import Linearizer
            k = Linearizer(ast, self.linearizer_opts)

            assert k.info.dtype == output.dtype, f"linearizer must match dtype. linearizer wants {k.info.dtype} but buffer is {output.dtype}"
            if not getenv("NOOPT"):
                if not k.apply_tensor_cores(getenv("TC", 1)): k.hand_coded_optimizations()
                if BEAM:
                    kb = Linearizer(ast, self.linearizer_opts)
                    kb.required_optimizations()
                    kb.dont_use_locals = bool(getenv("NOLOCALS"))
                    from .features.search import beam_search, time_linearizer
                    kb = beam_search(kb, rawbuffers, BEAM.value)
                    baseline = time_linearizer(
                        k,
                        rawbuffers,
                        allow_test_size=False,
                        disable_cache=True
                    )
                    beamtime = time_linearizer(
                        kb,
                        rawbuffers,
                        allow_test_size=False,
                        disable_cache=True,
                    )

                    if beamtime < baseline:
                        if DEBUG >= 1: print(
                            f"beam search {beamtime * 1e6:<12.2f} beat baseline {baseline * 1e6:<12.2f} by {baseline / beamtime:.2f}x")
                        k = kb
            return self.to_program(k)

        if getenv("ENABLE_METHOD_CACHE", 1):
            if ast not in self.method_cache:
                self.method_cache[ast] = get_program()
            prg = self.method_cache[ast]
        else:
            prg = get_program()

        if prg.name == getenv("PRINT_PRG", ''):
            print(prg.prg)

        prg.exec(
            rawbuffers,
            var_vals={k: var_vals[k] for k in ast_vars},
        )
        return output.realized
