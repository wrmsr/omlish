from __future__ import annotations

import abc
import collections
import functools
import itertools
import math
import random
import typing as ta

from omlish import collections as col  # noqa
from omlish import dataclasses as dc
from omlish import dispatch
from omlish import lang

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
    from .codegen.linearizer import Linearizer
    from .shape.shapetracker import ShapeTracker
    from .lazy import LazyBuffer


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


class ASTExecutor(lang.Abstract):

    @abc.abstractmethod
    def exec_ast(
            self,
            ast: LazyOp,
            output=None,
            inputs=None,
            var_vals=None,
            context=None,
            **kwargs,
    ) -> ta.Any:
        raise NotImplementedError


@functools.lru_cache(None)
def interpret_ast(device: Interpreted, ast: LazyOp) -> ta.Callable:
    tglob: dict[str, ta.Any] = {}
    lines: list[str] = []
    f = device.fxn_for_op

    @functools.lru_cache(None)
    def gstr(x: ta.Any, nm=None) -> str:
        ret = str(nm).replace(".", "_") if nm else f"m{len(tglob):04d}"
        tglob[ret] = x
        return ret

    @functools.lru_cache(None)
    def _interpret_ast(ast: LazyOp) -> str:
        if (
                ops.MulAcc in f
                and isinstance(ast, ops.Sum)
                and isinstance(ast.src[0], LazyOp)
                and isinstance(ast.src[0], ops.Mul)
        ):
            ast = ops.MulAcc(ast.src[0].src, ast.arg)

        if ops.AsStrided in f and isinstance(ast, ops.BufferOp):
            if isinstance(ast, ops.Const):
                tmp = f"{gstr(f[type(ast)], type(ast).__name__)}({gstr(ast.arg.val)}, {gstr(ast.arg.dtype)})"
            else:
                tmp = f"{gstr(f[type(ast)], type(ast).__name__)}(inputs[{ast.arg.idx - 1}])"
            for mop, arg in ast.arg.st.to_movement_ops():
                tmp = f"{gstr(f[mop], mop.__name__)}({tmp}, {gstr(arg)})"
        else:
            inp = [_interpret_ast(src) for src in ast.src]
            tmp = f"{gstr(f[type(ast)], type(ast).__name__)}({', '.join(inp + ([gstr(ast.arg)] if ast.arg else []))})"

        ret = f"a{len(lines)}"
        lines.append(f"  {ret} = {tmp}")
        return ret

    ret = _interpret_ast(ast)
    src = '\n'.join(
        ['def run(inputs):'] +
        lines +
        [
            f"  return {gstr(device.from_underlying, 'from_underlying')}({ret})"
            if device.from_underlying else
            f"  return {ret}"
        ]
    )

    if DEBUG >= 4:
        print(functools.reduce(lambda x, y: (x.replace(y[0], str(y[1])) if y[0][0:2] == "m0" else x), tglob.items(), src))

    exec(compile(src, "<ast>", "exec"), tglob)  # pylint: disable=exec-used

    return tglob['run']


class Interpreted(ASTExecutor):
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
        self.from_underlying = from_underlying
        self.synchronize = lambda: None
        self.codegen = None

    def exec_ast(self, ast: LazyOp, output=None, inputs=None, var_vals=None, context=None, **kwargs):
        ret = interpret_ast(self, ast)([x.realized for x in inputs] if inputs else None)

        if output is not None and ret.dtype != output.dtype and ops.Cast in self.fxn_for_op:
            # Do manual casting of ret if it does not match the required output dtype.
            ret = self.from_underlying(self.fxn_for_op[ops.Cast](self.to_underlying(ret), (output.dtype, False)))

        # TODO: is this used?
        if output is not None and output.output_buffer is not None:
            assert output.output_buffer.dtype == ret.dtype
            output.output_buffer._buf = ret._buf
            return output.output_buffer

        return ret


# --teenygrad--


@dc.dataclass(frozen=True)
class OpInfo:
    op: ops.Op

    shape: tuple[int, ...]
    dtype: DType
    flops: int
    mem: dict[int, int]

    @property
    def mem_estimate(self) -> int:
        return sum(self.mem.values()) + self.dtype.itemsize * prod(self.shape)


class OpAnalyzer:
    def __init__(self) -> None:
        super().__init__()

        self._dct: ta.MutableMapping[ta.Any, OpInfo] = {}  # col.IdentityKeyDict()

    def analyze(self, x: ta.Any) -> OpInfo:
        try:
            return self._dct[x]
        except KeyError:
            ret = self._analyze(x)
            self._dct[x] = dc.replace(ret, flops=0)
            return ret

    @dispatch.method
    def _analyze(self, op: ops.LazyOp) -> OpInfo:
        raise TypeError(op)

    @_analyze.register
    def _analyze_mem(self, op: ops.Mem) -> OpInfo:
        return OpInfo(op, op.arg.st.shape, op.arg.dtype, 0, {op.arg.idx: op.arg.dtype.itemsize * op.arg.st.size()})

    @_analyze.register
    def _analyze_const(self, op: ops.Const) -> OpInfo:
        return OpInfo(op, op.arg.st.shape, op.arg.dtype, 0, {})

    @_analyze.register
    def _analyze_cast(self, op: ops.Cast) -> OpInfo:
        xi = self.analyze(op.src[0])
        return OpInfo(op, xi.shape,  op.arg[0], xi.flops, xi.mem)

    @_analyze.register
    def _analyze_unary_op(self, op: ops.UnaryOp) -> OpInfo:
        xi = self.analyze(op.src[0])
        return OpInfo(op, xi.shape, xi.dtype, xi.flops + prod(xi.shape), xi.mem)

    @_analyze.register
    def _analyze_binary_op(self, op: ops.BinaryOp) -> OpInfo:
        xi, yi = map(self.analyze, op.src)
        return OpInfo(op, xi.shape, max(xi.dtype, yi.dtype), xi.flops + yi.flops + prod(xi.shape), {**xi.mem, **yi.mem})

    @_analyze.register
    def _analyze_reduce_op(self, op: ops.ReduceOp) -> OpInfo:
        xi = self.analyze(op.src[0])
        return OpInfo(op, op.arg, xi.dtype, xi.flops + prod(xi.shape), xi.mem)

    @_analyze.register
    def _analyze_where(self, op: ops.Where) -> OpInfo:
        xi, yi, zi = map(self.analyze, op.src)
        return OpInfo(op, xi.shape, yi.dtype, xi.flops + yi.flops + zi.flops + prod(xi.shape), {**xi.mem, **yi.mem, **zi.mem})


def get_lazyop_info(ast: LazyOp) -> OpInfo:
    return OpAnalyzer().analyze(ast)


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


class GraphBatchExecutor(BasicBatchExecutor):
    def __init__(self, jit_cache: list[tuple[ta.Any, ta.Any, ta.Any]]) -> None:
        super().__init__(jit_cache)
        self.graphs: list[ta.Any] = []

    def split_into_graphs(self, jit_cache: list[tuple[ta.Any, ta.Any, ta.Any]]):
        # Splitting the JIT cache into batches to enable parallel execution (cpu+gpu). Batch sizes follow a logarithmic
        # pattern: 4, 4, 8, 16, 32, and so on.
        # This helps push tasks to the GPU while the CPU updates the next graph.
        for i in range(2, max(math.ceil(math.log2(len(jit_cache))), 2) + 1):
            self.create_graph(jit_cache[(1 << (i - 1) if i > 2 else 0):(1 << i)])

    def exec(self, jit_cache: list[tuple[ta.Any, ta.Any, ta.Any]], updatable_entries):
        if not self.graphs:
            return super().exec(jit_cache, updatable_entries)  # No graph is created, switch to basic executor.
        update_keys_per_batch = collections.defaultdict(list)
        for j in updatable_entries.keys():
            update_keys_per_batch[max(0, math.ceil(math.log2(j + 1)) - 2)].append(j)
        for instid in range(len(self.graphs)):
            for jcid in update_keys_per_batch[instid]:
                self.update_node(
                    instid,
                    jcid,
                    jit_cache[jcid][0],
                    jit_cache[jcid][1],
                    jit_cache[jcid][2],
                    updated_args=updatable_entries[jcid],
                )
            self.exec_instance(instid)
        super().recalc_stat(jit_cache)

    def create_graph(self, jit_cache: list[tuple[ta.Any, ta.Any, ta.Any]]):
        raise NotImplementedError("must be implemented")

    def update_node(self, instid, jcid, prg, pargs, variables, updated_args=None):
        raise NotImplementedError("must be implemented")

    def exec_instance(self, instid):
        raise NotImplementedError("must be implemented")


class ASTRunner:
    def __init__(
            self,
            name: str,
            prg: str,
            global_size: ta.Optional[list[int]] = None,
            local_size: ta.Optional[list[int]] = None,
            op_estimate=0,
            mem_estimate=0,
            display_name: ta.Optional[str] = None,
            runtime_args: ta.Optional[dict] = None,
    ) -> None:
        super().__init__()
        if DEBUG >= 4:
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
            mem_estimate=k.info.mem_estimate,
            display_name=k.display_name,
            runtime_args={"binary": False},
        )

    def optimize_local_size(self, global_size: list[int], rawbufs: list[RawBuffer]) -> list[int]:
        assert self.global_size is not None, "needs a global size to optimize local size"
        test_rawbuffers = [type(rawbufs[0])(rawbufs[0].size, rawbufs[0].dtype), *rawbufs[1:]] \
            if rawbufs[0] in rawbufs[1:] else rawbufs
        MAX_WORKGROUP = self.clprg.max_work_group_size() if hasattr(self.clprg, 'max_work_group_size') else 1024
        local_dims = [[x for x in set([sz, 1, 2, 4, 8, 16, 32, 64, 128, 256, MAX_WORKGROUP]) if x <= sz] for sz in global_size]
        local_sizes = [list(x) for x in itertools.product(*local_dims) if prod(x) <= MAX_WORKGROUP] * 2  # try each valid size twice

        def try_exec(local_size):
            try:
                return self.clprg(
                    [g // l if g % l == 0 else g / l for g, l in zip(global_size, local_size)],
                    local_size,
                    *test_rawbuffers,
                    wait=True,
                )
            except Exception:
                return float('inf')

        return min([(try_exec(local_size), local_size) for local_size in random.sample(local_sizes, len(local_sizes))])[1]

    def build(self, compiler, runtime, batch_exec=BasicBatchExecutor):
        self.lib = compiler.__wrapped__(self.prg) if getenv("DISABLE_COMPILER_CACHE") else compiler(self.prg)
        self.clprg, self.batch_exec = runtime(self.name, self.lib, **self.runtime_args), batch_exec
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
            # TODO: this is copied from get_program
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


class Compiled(ASTExecutor):
    def __init__(
            self,
            buffer: type[RawBuffer],
            linearizer_opts,
            renderer,
            compiler,
            runtime,
            synchronize=lambda: None,
            batch_exec=BasicBatchExecutor,
    ) -> None:
        super().__init__()
        self.buffer = buffer
        self.linearizer_opts = linearizer_opts
        self.renderer = renderer
        self.runtime = runtime
        self.compiler = compiler
        self.synchronize = synchronize
        self.batch_exec = batch_exec
        self.method_cache: dict[LazyOp, ASTRunner] = {}

    def to_program(self, k: Linearizer) -> ASTRunner:
        k.linearize()

        src, runtime_args = self.renderer(k.function_name, k.uops)
        return ASTRunner(
            k.function_name,
            src,
            k.global_size,
            k.local_size,
            op_estimate=k.info.flops,
            mem_estimate=k.info.mem_estimate,
            display_name=k.display_name,
            runtime_args=runtime_args
        ).build(
            self.compiler,
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
                if not (used_tensor_cores := k.apply_tensor_cores(getenv("TC", 1))):
                    k.hand_coded_optimizations()

                if BEAM >= 1 and not vars_from_ast(ast):
                    lins = [(("tc" if used_tensor_cores else "hc"), k)]

                    # allocate a scratch buffer if output buffer is also input
                    test_rawbuffers = [type(rawbuffers[0])(rawbuffers[0].size, rawbuffers[0].dtype), *rawbuffers[1:]] \
                        if rawbuffers[0] in rawbuffers[1:] else rawbuffers
                    kb = Linearizer(ast, self.linearizer_opts)
                    kb.required_optimizations()
                    from .features.search import beam_search
                    from .features.search import time_linearizer

                    lins.append((
                        f"beam{BEAM.value}",
                        beam_search(
                            kb,
                            test_rawbuffers,
                            BEAM.value,
                            bool(getenv("BEAM_ESTIMATE", 1)),
                        ),
                    ))

                    if used_tensor_cores:
                        lins.append(("hc", Linearizer(ast, self.linearizer_opts)))
                        lins[-1][1].hand_coded_optimizations()
                    timed = sorted(
                        [
                            (
                                nm,
                                tk,
                                time_linearizer(
                                    tk,
                                    test_rawbuffers,
                                    allow_test_size=False,
                                    disable_cache=True,
                                    clear_l2=True,
                                ),
                            )
                            for nm, tk in lins
                        ],
                        key=lambda x: x[2],
                    )

                    if DEBUG >= 1:
                        print("  <  ".join(
                            f"{nm:6s} : {lin.colored_shape(30, dense=True)} : {tm * 1e6:8.2f} us"
                            for nm, lin, tm in timed
                        ))

                    k = timed[0][1]

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
