from __future__ import annotations

import abc
import functools
import re
import time
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
from .helpers import NOOPT
from .helpers import all_int
from .helpers import ansilen
from .helpers import colored
from .helpers import getenv
from .helpers import prod
from .ops import LazyOp
from .runtime.lib import RawBuffer
from .shape.symbolic import NumNode
from .shape.symbolic import Variable
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
    val: ta.Any
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
        name,
        op_estimate,
        mem_estimate,
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


# **************** batch executor ****************


@dc.dataclass(frozen=True)
class JitItem:
    prg: AstRunner
    rawbufs: list[ta.Optional[RawBuffer]]


class BatchExecutor:
    def __init__(
            self,
            jit_cache: list[JitItem],
            input_rawbuffers: dict[ta.Union[int, str], RawBuffer],
            var_vals: dict[Variable, int],
    ) -> None:
        super().__init__()
        self.jit_cache: list[JitItem] = jit_cache
        self.input_replace: dict[tuple[int, int], ta.Union[int, str]] = {}
        self.op_estimate = NumNode(0)
        self.mem_estimate = NumNode(0)
        for j, ji in enumerate(jit_cache):
            if isinstance(ji.prg, AstRunner):  # TODO: this is just for world and needs to be refactored
                self.op_estimate += ji.prg.op_estimate
                self.mem_estimate += ji.prg.mem_estimate
            for i, a in enumerate(ji.rawbufs):
                if a in [v for v in input_rawbuffers.values()]:
                    self.input_replace[(j, i)] = [k for k, v in input_rawbuffers.items() if v == a][0]
        assert set(self.input_replace.values()) == set(input_rawbuffers.keys()), "some input tensors not found"
        self.clear_jit_inputs()

    def __call__(
            self,
            input_rawbuffers: dict[ta.Union[int, str], RawBuffer],
            var_vals: dict[Variable, int],
            wait=False,
    ):
        for (j, i), input_name in self.input_replace.items():
            self.jit_cache[j].rawbufs[i] = input_rawbuffers[input_name]

        for ji in self.jit_cache:
            ji.prg(ji.rawbufs, var_vals, jit=True)

        self.clear_jit_inputs()

    def clear_jit_inputs(self):
        for (j, i) in self.input_replace.keys():
            self.jit_cache[j].rawbufs[i] = None


class AstRunner:
    def __init__(self, ast: ta.Optional[LazyOp]) -> None:
        super().__init__()
        if ast is None:
            self.op_estimate= 0
            self.mem_estimate= 0
            self.vars = []
        else:
            info = get_lazyop_info(ast)
            self.op_estimate = info.flops
            self.mem_estimate = info.mem_estimate
            from .lazy import vars_from_ast
            self.vars = vars_from_ast(ast)
            assert all(v._val is None for v in self.vars), f"AstRunner contains bound Variable {self.vars}"

    def exec(
            self,
            rawbufs: list[ta.Optional[RawBuffer]],
            var_vals: ta.Optional[dict[Variable, int]] = None,
            force_wait=False,
    ) -> ta.Optional[float]:
        from .jit import CacheCollector
        et = self(rawbufs, var_vals, force_wait=force_wait)
        CacheCollector.add(self, rawbufs, var_vals if var_vals is not None else {})
        return et

    def __call__(
            self,
            rawbufs: list[ta.Optional[RawBuffer]],
            var_vals: ta.Optional[dict[Variable, int]] = None,
            jit=False,
            force_wait=False,
    ) -> ta.Optional[float]:
        raise NotImplementedError("override this")


# **************** for Interpreted Buffers ****************


class InterpretedAstRunner(AstRunner):
    def __init__(self, ast: LazyOp, fxn: ta.Callable) -> None:
        self.fxn = fxn
        super().__init__(ast)

    def __call__(
            self,
            rawbufs: list[ta.Optional[RawBuffer]],
            var_vals: ta.Optional[dict[Variable, int]] = None,
            jit=False,
            force_wait=False,
    ) -> float:
        st = time.perf_counter()
        ret: RawBuffer = self.fxn(rawbufs[1:], var_vals)
        et = time.perf_counter() - st
        update_stats(f"<interpreted {ret.size}>", self.op_estimate, self.mem_estimate, var_vals, et, len(rawbufs), jit)
        if rawbufs[0] is not None:
            assert rawbufs[0].dtype == ret.dtype
            rawbufs[0].size = ret.size  # NOTE: for symbolic this can change
            rawbufs[0]._buf = ret._buf
        else:
            rawbufs[0] = ret
        return et


class Interpreted:
    def __init__(
            self,
            buffer: type[RawBuffer],
            fxn_for_op: dict[type[ops.LazyOp], ta.Callable],
            from_underlying: ta.Optional[ta.Callable] = None,
    ) -> None:
        super().__init__()
        self.buffer = buffer
        self.fxn_for_op = fxn_for_op
        self.from_underlying = from_underlying
        self.synchronize = lambda: None
        self.batch_executor = BatchExecutor
        self.codegen = None
        self.method_cache: dict[LazyOp, InterpretedAstRunner] = {}

    def exec_ast(
            self,
            ast: LazyOp,
            output: LazyBuffer,
            inputs: tuple[LazyBuffer, ...],
            var_vals: dict[Variable, int],
            **kwargs,
    ):
        if ast not in self.method_cache:
            self.method_cache[ast] = get_interpreted_fxn(
                self.fxn_for_op,
                self.from_underlying,
                ast,
            )
        rawbufs = [output.realized if output.realized is not None else output.output_buffer] + \
                  [x.realized for x in inputs]
        self.method_cache[ast].exec(rawbufs, var_vals)
        output.realized = rawbufs[0]


def get_interpreted_fxn(
        fxn_for_op: dict[type[ops.LazyOp], ta.Callable],
        from_underlying: ta.Optional[ta.Callable],
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
            inp = [_interpret_ast(src) for src in ast.src]
            tmp = f"{gstr(fxn_for_op[type(ast)], type(ast).__name__)}({', '.join(inp + ([gstr(ast.arg)] if ast.arg else []))})"

        ret = f"a{len(lines)}"
        lines.append(f"  {ret} = {tmp}")
        return ret

    ret = _interpret_ast(ast)
    src = '\n'.join(
        ['def run(inputs, var_vals):'] +
        lines +
        [
            f"  return {gstr(from_underlying, 'from_underlying')}({ret})"
            if from_underlying is not None else
            f"  return {ret}"
        ]
    )

    if DEBUG >= 4:
        print(
            functools.reduce(lambda x, y: (x.replace(y[0], str(y[1])) if y[0][0:2] == "m0" else x), tglob.items(), src))

    exec(compile(src, "<ast>", "exec"), tglob)  # pylint: disable=exec-used
    return InterpretedAstRunner(ast, tglob['run'])


# **************** for Compiled Buffers ****************


class CompiledAstRunner(AstRunner):
    def __init__(
            self,
            ast: ta.Optional[LazyOp],
            name: str,
            prg: str,
            global_size: ta.Optional[list[int]] = None,
            local_size: ta.Optional[list[int]] = None,
            op_estimate=0,
            mem_estimate=0,
            display_name: ta.Optional[str] = None,
            runtime_args: ta.Optional[dict] = None,
    ) -> None:
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
        super().__init__(ast)

    def build(self, compiler, runtime):
        self.lib = compiler.__wrapped__(self.prg) if getenv("DISABLE_COMPILER_CACHE") else compiler(self.prg)
        self.clprg = runtime(self.name, self.lib)
        return self

    def launch_dims(self, var_vals):
        if self.global_size is not None:
            global_size = ([sym_infer(sz, var_vals) for sz in self.global_size] + [1] * (3 - len(self.global_size)))
        else:
            global_size = self.global_size
        if self.local_size is not None:
            local_size = ([sym_infer(sz, var_vals) for sz in self.local_size] + [1] * (3 - len(self.local_size)))
        else:
            local_size = self.local_size
        return global_size, local_size

    def __call__(
            self,
            rawbufs: list[ta.Optional[RawBuffer]],
            var_vals: ta.Optional[dict[Variable, int]] = None,
            jit=False,
            force_wait=False,
    ) -> ta.Optional[float]:
        if var_vals is None:
            var_vals = {}
        var_vals = {k: var_vals[k] for k in self.vars}  # filter the var_vals

        global_size, local_size = self.launch_dims(var_vals)

        if global_size is not None and local_size is None and all_int(self.global_size):  # type: ignore[arg-type]
            # TODO: this is copied from get_program
            from .features.search import optimize_local_size
            local_size = self.local_size = optimize_local_size(self.clprg, global_size, ta.cast(list[RawBuffer], rawbufs))
            global_size = self.global_size = [g // l if g % l == 0 else g / l for g, l in zip(global_size, local_size)]

        lra = self.runtime_args.copy()
        if global_size:
            lra['global_size'] = global_size
        if local_size and 'local_size' not in lra:
            lra['local_size'] = local_size

        et = self.clprg(*rawbufs, *var_vals.values(), **lra, wait=force_wait or DEBUG >= 2)

        update_stats(
            self.display_name if self.display_name is not None else self.name,
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
            batch_executor=BatchExecutor,
    ) -> None:
        super().__init__()
        self.buffer = buffer
        self.linearizer_opts = linearizer_opts
        self.renderer = renderer
        self.compiler = compiler
        self.runtime = runtime
        self.synchronize = synchronize
        self.batch_executor = BatchExecutor if getenv("JIT") == 2 else batch_executor
        self.method_cache: dict[LazyOp, CompiledAstRunner] = {}

    def to_program(self, k: Linearizer) -> CompiledAstRunner:
        k.linearize()
        src, runtime_args = self.renderer(k.function_name, k.uops)
        return CompiledAstRunner(
            k.ast,
            k.function_name,
            src,
            k.global_size,
            k.local_size,
            display_name=k.display_name,
            runtime_args=runtime_args,
        ).build(
            self.compiler,
            self.runtime,
        )

    def exec_ast(
            self,
            ast: LazyOp,
            output: LazyBuffer,
            inputs: tuple[LazyBuffer, ...],
            var_vals: dict[Variable, int],
            **kwargs,
    ):
        # check if we can reuse the output buffer
        # if it's aliased, don't use it
        # TODO: this is pretty wrong actually, who knows where else this buffer is used?
        # TODO: what if an assign is required? this silently is wrong
        output.realized = output.output_buffer
        if output.realized is not None:
            for i, a in enumerate(inputs):
                # TODO: if this is contiguous it's fine
                if a.realized == output.realized:
                    if any(
                            not x.arg.st.contiguous
                            for x in ast.get_lazyops()
                            if isinstance(x, ops.Mem)
                               and x.arg.idx == i + 1
                    ):
                        output.realized = None
                        break

        # we don't have an output buffer, we have to create it, and create to max size if it has symbolic shape
        if output.realized is None:
            output.realized = self.buffer(
                prod((s if isinstance(s, int) else s.max for s in output.shape)),
                output.dtype,
                **kwargs,
            )
            if output.realized.size == 0:
                return output.realized

        # all the rawbuffers
        rawbuffers = [output.realized] + [x.realized for x in inputs]

        if ast not in self.method_cache:
            self.method_cache[ast] = get_optimized_program(self.linearizer_opts, self.to_program, ast, rawbuffers)

        self.method_cache[ast].exec(rawbuffers, var_vals)


def get_optimized_program(
        linearizer_opts: LinearizerOptions,
        to_program,
        ast: LazyOp,
        rawbuffers: list[RawBuffer],
) -> CompiledAstRunner:
    if DEBUG >= 3:
        from .lazy import print_tree
        print_tree(ast)

    from .codegen.linearizer import Linearizer

    k = Linearizer(ast, linearizer_opts)

    assert (
        k.info.dtype == rawbuffers[0].dtype
    ), f"linearizer must match dtype. linearizer wants {k.info.dtype} but buffer is {rawbuffers[0].dtype}"

    if not NOOPT:
        if not (used_tensor_cores := k.apply_tensor_cores(getenv("TC", 1))):
            k.hand_coded_optimizations()

        if BEAM >= 1:
            lins = [(("tc" if used_tensor_cores else "hc"), k)]
            # allocate a scratch buffer if output buffer is also input
            test_rawbuffers = [type(rawbuffers[0])(rawbuffers[0].size, rawbuffers[0].dtype), *rawbuffers[1:]] \
                if rawbuffers[0] in rawbuffers[1:] else rawbuffers

            kb = Linearizer(ast, linearizer_opts)
            kb.required_optimizations()

            from .features.search import beam_search, time_linearizer
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
    else:
        k.required_optimizations()

    return to_program(k)
