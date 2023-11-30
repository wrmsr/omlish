from __future__ import annotations

import functools
import re
import time
import typing as ta

from omlish import collections as col  # noqa
from omlish import dataclasses as dc
from omlish import dispatch

from . import ops
from .dtypes import DType
from .helpers import BEAM
from .helpers import DEBUG
from .helpers import GlobalCounters
from .helpers import NOOPT
from .helpers import all_int
from .helpers import ansilen
from .helpers import colored
from .helpers import getenv
from .helpers import prod
from .helpers import to_function_name
from .ops import LazyOp
from .runtime.lib import RawBuffer
from .shape.symbolic import Variable
from .shape.symbolic import sint
from .shape.symbolic import sym_infer

if ta.TYPE_CHECKING:
    from .codegen.kernel import LinearizerOptions
    from .codegen.linearizer import Linearizer
    from .lazy import LazyBuffer
    from .shape.shapetracker import ShapeTracker


@dc.dataclass(frozen=True)
class MemBuffer:
    idx: int
    dtype: DType
    st: ShapeTracker


@dc.dataclass(frozen=True)
class ConstBuffer:
    val: int | float
    dtype: DType
    st: ShapeTracker


@dc.dataclass(frozen=True)
class ScheduleItem:
    ast: LazyOp
    out: LazyBuffer
    inputs: tuple[LazyBuffer, ...]
    var_vals: dict[Variable, int]


# **************** independent FlopCounter ****************


@dc.dataclass(frozen=True)
class OpInfo:
    op: LazyOp

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


# **************** GlobalCounters stats ****************


def update_stats(
        name: str,
        op_estimate: sint,
        mem_estimate: sint,
        var_vals: ta.Optional[dict[Variable, int]],
        et: ta.Optional[float],
        buf_count,
        jit=False,
        num_kernels=1,
        lra=None,
):
    if var_vals is None:
        var_vals = {}

    op_estimate, mem_estimate = sym_infer(op_estimate, var_vals), sym_infer(mem_estimate, var_vals)
    if DEBUG >= 2:
        print(
            f"{colored(f'*** {GlobalCounters.kernel_count:4d}', ('magenta' if num_kernels == 1 else 'CYAN') if jit else None)} "
            f"{name+' '*(37-ansilen(name))} "
            f"arg {buf_count:3d} "
            f"sz {str(lra.get('global_size', '') if lra else ''):18s} {str(lra.get('local_size', '') if lra else ''):12s} "
            f"OPs {int(op_estimate/1e6):6d}M/{GlobalCounters.global_ops/1e9:7.2f}G  "
            f"mem {GlobalCounters.mem_used/1e9:5.2f} GB " +
            (
                str() if et is None else
                (
                    f"tm {et*1e6:9.2f}us/{GlobalCounters.time_sum_s*1e3:9.2f}ms "
                    f"({op_estimate/((et or 1e-20)*1e9):8.2f} GFLOPS, {mem_estimate/((et or 1e-20)*1e9):7.2f} GB/s)"
                )
            )
        )

    GlobalCounters.kernel_count += num_kernels
    GlobalCounters.global_ops += op_estimate
    GlobalCounters.global_mem += mem_estimate

    if et is not None:
        GlobalCounters.time_sum_s += et


# **************** shared Runner that can go in the JIT ****************


class JitRunner:
    def __init__(self) -> None:
        super().__init__()
        self.op_estimate = 0
        self.mem_estimate = 0

    def exec(
            self,
            rawbufs: list[RawBuffer],
            var_vals: ta.Optional[dict[Variable, int]] = None,
    ) -> ta.Optional[float]:
        var_vals = var_vals if var_vals is not None else {}
        from .jit import CacheCollector
        et = self(rawbufs, var_vals)
        CacheCollector.add(self, rawbufs, var_vals)
        return et

    def __call__(
            self,
            rawbufs: list[RawBuffer],
            var_vals: dict[Variable, int],
            wait=False,
            jit=False,
    ) -> ta.Optional[float]:
        raise NotImplementedError("override this")


# **************** for Interpreted Buffers ****************


class InterpretedAstRunner(JitRunner):
    def __init__(self, ast: LazyOp, fxn: ta.Callable) -> None:
        super().__init__()
        self.fxn = fxn
        info = get_lazyop_info(ast)
        self.op_estimate = info.flops
        self.mem_estimate = info.mem_estimate

    def __call__(
            self,
            rawbufs: list[RawBuffer],
            var_vals: dict[Variable, int],
            wait=False,
            jit=False,
    ) -> float:
        st = time.perf_counter()
        ret: RawBuffer = self.fxn(rawbufs[1:], var_vals)
        et = time.perf_counter() - st
        update_stats(f"<interpreted {ret.size}>", self.op_estimate, self.mem_estimate, var_vals, et, len(rawbufs), jit)
        assert rawbufs[0].dtype == ret.dtype, f"dtype mismatch in Interpreted, {rawbufs[0].dtype=} != {ret.dtype=}"
        rawbufs[0].dtype = ret.dtype
        rawbufs[0].size = ret.size
        rawbufs[0]._buf = ret._buf
        rawbufs[0].offset = ret.offset
        return et


class Interpreted:
    def __init__(
            self,
            buffer: type[RawBuffer],
            fxn_for_op: dict[type[ops.LazyOp], ta.Callable],
    ) -> None:
        super().__init__()
        self.buffer = buffer
        self.fxn_for_op = fxn_for_op
        self.synchronize = lambda: None
        self.codegen = None
        self.graph = None
        self.method_cache: dict[LazyOp, InterpretedAstRunner] = {}

    def allocate_output(self, ast: LazyOp, output: LazyBuffer, inputs: tuple[LazyBuffer, ...]):
        output.realized = output.output_buffer if output.output_buffer is not None else self.buffer.__new__(self.buffer)

    @functools.lru_cache(None)    # pylint: disable=method-cache-max-size-none
    def get_runner(self, ast: LazyOp) -> InterpretedAstRunner:
        return _get_interpreted_fxn(self.fxn_for_op, ast)


def _get_interpreted_fxn(
        fxn_for_op: dict[type[ops.LazyOp], ta.Callable],
        ast: LazyOp,
) -> InterpretedAstRunner:
    if DEBUG >= 3:
        from .lazy import print_tree
        print_tree(ast)

    tglob: dict[str, ta.Any] = {"Variable": Variable}
    lines: list[str] = []

    @functools.lru_cache(None)
    def gstr(x: ta.Any, nm=None) -> str:
        if ('Variable' in (str_arg := repr(x)) or 'NumNode' in str_arg):
            str_arg = re.sub(r'Variable\(.*?\)', lambda m: f'var_vals[{str(m.group(0))}]', str_arg)
            # TODO: (Variable - Variable) might create NumNode. can we remove it?
            return re.sub(r'NumNode\((.*?)\)', r'\1', str_arg)

        ret = str(nm).replace(".", "_") if nm else f"m{len(tglob):04d}"
        tglob[ret] = x
        return ret

    @functools.lru_cache(None)
    def _interpret_ast(ast: LazyOp) -> str:
        if (
                ops.MulAcc in fxn_for_op
                and isinstance(ast, ops.Sum)
                and isinstance(ast.src[0], LazyOp)
                and isinstance(ast.src[0], ops.Mul)
        ):
            ast = ops.MulAcc(ast.src[0].src, ast.arg)

        if isinstance(ast, ops.BufferOp):
            if isinstance(ast, ops.Const):
                tmp = f"{gstr(fxn_for_op[type(ast)], type(ast).__name__)}({gstr(ast.arg.val)}, {gstr(ast.arg.dtype)})"
            else:
                tmp = f"{gstr(fxn_for_op[type(ast)], type(ast).__name__)}(inputs[{ast.arg.idx - 1}])"
            for mop, arg in ast.arg.st.to_movement_ops():
                tmp = f"{gstr(fxn_for_op[mop], mop.__name__)}({tmp}, {gstr(arg)})"

        else:
            tmp = (
                f"{gstr(fxn_for_op[type(ast)], type(ast).__name__)}("
                f"{', '.join([_interpret_ast(src) for src in ast.src] + ([gstr(ast.arg)] if ast.arg else []))}"
                f")"
            )

        ret = f"a{len(lines)}"
        lines.append(f"  {ret} = {tmp}")
        return ret

    ret = _interpret_ast(ast)
    src = '\n'.join(
        ['def run(inputs, var_vals):'] +
        lines +
        [
            f"  return {gstr(fxn_for_op[ops.FromUnderlying], ops.FromUnderlying.__name__)}({ret})"
            if ops.FromUnderlying in fxn_for_op else
            f"  return {ret}"
        ]
    )

    if DEBUG >= 4:
        print(
            functools.reduce(lambda x, y: (x.replace(y[0], str(y[1])) if y[0][0:2] == "m0" else x), tglob.items(), src))

    exec(compile(src, "<ast>", "exec"), tglob)  # pylint: disable=exec-used
    return InterpretedAstRunner(ast, tglob['run'])


# **************** for Compiled Buffers ****************


class CompiledAstRunner(JitRunner):
    def __init__(
            self,
            ast: ta.Optional[LazyOp],
            name: str,
            prg: str,
            global_size: ta.Optional[list[int]] = None,
            local_size: ta.Optional[list[int]] = None,
            runtime_args: ta.Optional[dict] = None,
    ) -> None:
        super().__init__()
        if DEBUG >= 4:
            print(prg)
        if global_size is not None:
            global_size = global_size + [1] * (3 - len(global_size))
        if local_size is not None:
            local_size = local_size + [1] * (3 - len(local_size))
        self.name = name
        self.display_name = to_function_name(name)
        self.prg = prg
        self.global_size = global_size
        self.local_size = local_size
        self.runtime_args = runtime_args if runtime_args is not None else {}
        self.vars: list[Variable] = []
        if ast:
            info = get_lazyop_info(ast)
            self.op_estimate = info.flops
            self.mem_estimate = info.mem_estimate
            from .lazy import vars_from_ast
            self.vars = vars_from_ast(ast)
            assert all(v._val is None for v in self.vars), f"ASTRunner contains bound Variable {self.vars}"

    def build(self, compiler, runtime):
        self.lib = compiler.__wrapped__(self.prg) if getenv("DISABLE_COMPILER_CACHE") else compiler(self.prg)
        self.clprg = runtime(self.name, self.lib)
        return self

    def launch_dims(self, var_vals):
        if self.global_size is not None:
            global_size = [sym_infer(sz, var_vals) for sz in self.global_size]
        else:
            global_size = self.global_size
        if self.local_size is not None:
            local_size = [sym_infer(sz, var_vals) for sz in self.local_size]
        else:
            local_size = self.local_size
        return global_size, local_size

    def __call__(
            self,
            rawbufs: list[RawBuffer],
            var_vals: dict[Variable, int],
            wait=False,
            jit=False,
    ) -> ta.Optional[float]:
        global_size, local_size = self.launch_dims(var_vals)

        if global_size is not None and local_size is None and all_int(self.global_size):  # type: ignore[arg-type]
            # TODO: this is copied from get_program
            from .features.search import optimize_local_size
            local_size = self.local_size = optimize_local_size(self.clprg, global_size, rawbufs)
            global_size = self.global_size = [g // l if g % l == 0 else g / l for g, l in zip(global_size, local_size)]

        lra = self.runtime_args.copy()
        if global_size:
            lra['global_size'] = global_size
        if local_size and 'local_size' not in lra:
            lra['local_size'] = local_size

        et = self.clprg(*rawbufs, *[var_vals[k] for k in self.vars], **lra, wait=wait or DEBUG >= 2)

        update_stats(
            self.display_name,
            self.op_estimate,
            self.mem_estimate,
            var_vals,
            et,
            len(rawbufs),
            jit,
            lra=lra,
        )

        return et


class Compiled:
    def __init__(
            self,
            buffer: type[RawBuffer],
            linearizer_opts: LinearizerOptions,
            renderer,
            compiler,
            runtime,
            synchronize=lambda: None,
            graph=None,
    ) -> None:
        super().__init__()
        self.buffer = buffer
        self.linearizer_opts = linearizer_opts
        self.renderer = renderer
        self.compiler = compiler
        self.runtime = runtime
        self.synchronize = synchronize
        self.graph = graph

    def to_program(self, k: Linearizer) -> CompiledAstRunner:
        k.linearize()
        src, runtime_args = self.renderer(to_function_name(k.name), k.uops)
        return CompiledAstRunner(
            k.ast,
            k.name,
            src,
            k.global_size,
            k.local_size,
            runtime_args,
        ).build(
            self.compiler,
            self.runtime,
        )

    @functools.lru_cache(None)  # pylint: disable=method-cache-max-size-none
    def get_runner(self, ast: LazyOp) -> CompiledAstRunner:
        return self.to_program(_get_optimized_linearizer(self.linearizer_opts, ast))


def _get_optimized_linearizer(
        linearizer_opts: LinearizerOptions,
        ast: LazyOp,
) -> Linearizer:
    if DEBUG >= 3:
        from .lazy import print_tree
        print_tree(ast)

    from .codegen.linearizer import Linearizer

    k = Linearizer(ast, linearizer_opts)

    if not NOOPT:
        if not (used_tensor_cores := k.apply_tensor_cores(getenv("TC", 1))):
            k.hand_coded_optimizations()

        if BEAM >= 1:
            lins = [(("tc" if used_tensor_cores else "hc"), k)]

            kb = Linearizer(ast, linearizer_opts)
            kb.required_optimizations()

            from .features.search import beam_search, time_linearizer, bufs_from_lin
            # TODO: this shouldn't use Device.DEFAULT, it should get the device from the LinearizerOptions
            test_rawbuffers = bufs_from_lin(kb)  # allocate scratch buffers for optimization

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
                lins.append(("hc", Linearizer(ast, linearizer_opts)))
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
    else:
        k.required_optimizations()

    return k
