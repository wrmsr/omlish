from __future__ import annotations

import functools
import importlib
import inspect
import pathlib
import re
import time
from typing import Any
from typing import Callable
from typing import Dict
from typing import List
from typing import Optional
from typing import TYPE_CHECKING
from typing import Type
from typing import Union

from .helpers import BEAM
from .helpers import DEBUG
from .helpers import GlobalCounters
from .helpers import NOOPT
from .helpers import all_int
from .helpers import ansilen
from .helpers import colored
from .helpers import getenv
from .helpers import to_function_name
from .ops import BinaryOps
from .ops import BufferOps
from .ops import LazyOp
from .ops import Op
from .ops import ReduceOps
from .ops import TernaryOps
from .ops import get_lazyop_info
from .runtime.lib import RawBuffer
from .shape.symbolic import Variable
from .shape.symbolic import sint
from .shape.symbolic import sym_infer

if TYPE_CHECKING:
    from .codegen.linearizer import Linearizer
    from .codegen.kernel import LinearizerOptions

# **************** Device ****************


class _Device:
    def __init__(self) -> None:
        self._buffers: List[str] = [
            x.stem[len("ops_") :].upper()
            for x in (pathlib.Path(__file__).parent / "runtime").iterdir()
            if x.stem.startswith("ops_")
        ]

    def canonicalize(self, device: Optional[str]) -> str:
        return (
            (
                device.split(":", 1)[0].upper()
                + ((":" + device.split(":", 1)[1]) if ":" in device else "")
            ).replace(":0", "")
            if device is not None
            else self.DEFAULT
        )

    @functools.lru_cache(
        maxsize=None
    )  # this class is a singleton, pylint: disable=method-cache-max-size-none
    def __getitem__(self, x: str) -> Union[Interpreted, Compiled]:
        x = x.split(":")[0].upper()
        return [
            cls
            for cname, cls in inspect.getmembers(
                importlib.import_module(f".runtime.ops_{x.lower()}", __package__)
            )
            if (cname.lower() == x.lower() + "device") and x in self._buffers
        ][0]

    @functools.cached_property
    def DEFAULT(self) -> str:
        device_from_env: Optional[str] = functools.reduce(lambda val, ele: ele if getenv(ele) == 1 else val, self._buffers, None)  # type: ignore
        if device_from_env:
            return device_from_env
        for device in ["METAL", "CUDA", "GPU"]:
            try:
                if self[device]:
                    return device
            except Exception:
                pass
        return "CPU"


Device = _Device()

# **************** shared device helpers ****************


class JITRunner:
    def __init__(self):
        self.op_estimate, self.mem_estimate = 0, 0

    def exec(
        self, rawbufs: List[RawBuffer], var_vals: Optional[Dict[Variable, int]] = None
    ) -> Optional[float]:
        var_vals = var_vals if var_vals is not None else {}
        from .jit import CacheCollector

        et = self(rawbufs, var_vals)
        CacheCollector.add(self, rawbufs, var_vals)
        return et

    def __call__(
        self,
        rawbufs: List[RawBuffer],
        var_vals: Dict[Variable, int],
        wait=False,
        jit=False,
    ) -> Optional[float]:
        raise NotImplementedError("override this")


def update_stats(
    name: str,
    op_estimate: sint,
    mem_estimate: sint,
    var_vals: Optional[Dict[Variable, int]],
    et: Optional[float],
    buf_count,
    jit=False,
    num_kernels=1,
    lra: Optional[Dict] = None,
):
    if var_vals is None:
        var_vals = {}
    op_estimate, mem_estimate = sym_infer(op_estimate, var_vals), sym_infer(
        mem_estimate, var_vals
    )
    if DEBUG >= 2:
        print(
            f"{colored(f'*** {GlobalCounters.kernel_count:4d}', ('magenta' if num_kernels == 1 else 'CYAN') if jit else None)} {name+' '*(37-ansilen(name))} arg {buf_count:3d} sz {str(lra.get('global_size', '') if lra else ''):18s} {str(lra.get('local_size', '') if lra else ''):12s} OPs {int(op_estimate/1e6):6d}M/{GlobalCounters.global_ops/1e9:7.2f}G  mem {GlobalCounters.mem_used/1e9:5.2f} GB "
            + (
                str()
                if et is None
                else f"tm {et*1e6:9.2f}us/{GlobalCounters.time_sum_s*1e3:9.2f}ms ({op_estimate/((et or 1e-20)*1e9):8.2f} GFLOPS, {mem_estimate/((et or 1e-20)*1e9):7.2f} GB/s)"
            )
        )
    GlobalCounters.kernel_count += num_kernels
    GlobalCounters.global_ops += op_estimate
    GlobalCounters.global_mem += mem_estimate
    if et is not None:
        GlobalCounters.time_sum_s += et


# **************** for Interpreted Devices ****************


class InterpretedASTRunner(JITRunner):
    def __init__(self, ast: LazyOp, fxn: Callable):
        super().__init__()
        self.fxn = fxn
        info = get_lazyop_info(ast)
        self.op_estimate, self.mem_estimate = info.flops, info.mem_estimate

    def __call__(
        self,
        rawbufs: List[RawBuffer],
        var_vals: Dict[Variable, int],
        wait=False,
        jit=False,
    ) -> float:
        st = time.perf_counter()
        ret: RawBuffer = self.fxn(rawbufs[1:], var_vals)
        et = time.perf_counter() - st
        update_stats(
            f"<interpreted {ret.size}>",
            self.op_estimate,
            self.mem_estimate,
            var_vals,
            et,
            len(rawbufs),
            jit,
        )
        assert (
            rawbufs[0].dtype == ret.dtype
        ), f"dtype mismatch in Interpreted, {rawbufs[0].dtype=} != {ret.dtype=}"
        rawbufs[0].dtype, rawbufs[0].size, rawbufs[0]._buf, rawbufs[0].offset = (
            ret.dtype,
            ret.size,
            ret._buf,
            ret.offset,
        )
        return et


class Interpreted:
    def __init__(self, buffer: Type[RawBuffer], fxn_for_op: Dict[Op, Callable]):
        self.buffer, self.fxn_for_op = buffer, fxn_for_op
        self.synchronize, self.codegen, self.graph = lambda: None, None, None

    @functools.lru_cache(None)  # pylint: disable=method-cache-max-size-none
    def get_runner(self, ast: LazyOp) -> InterpretedASTRunner:
        return _get_interpreted_fxn(self.fxn_for_op, ast)


def _get_interpreted_fxn(
    fxn_for_op: Dict[Op, Callable], ast: LazyOp
) -> InterpretedASTRunner:
    if DEBUG >= 3:
        from .graph import print_tree

        print_tree(ast)
    tglob: Dict[str, Any] = {"Variable": Variable}
    lines: List[str] = []

    @functools.lru_cache(None)
    def gstr(x: Any, nm=None) -> str:
        if "Variable" in (str_arg := repr(x)) or "NumNode" in str_arg:
            str_arg = re.sub(
                r"Variable\(.*?\)", lambda m: f"var_vals[{str(m.group(0))}]", str_arg
            )
            # TODO: (Variable - Variable) might create NumNode. can we remove it?
            return re.sub(r"NumNode\((.*?)\)", r"\1", str_arg)
        ret = str(nm).replace(".", "_") if nm else f"m{len(tglob):04d}"
        tglob[ret] = x
        return ret

    @functools.lru_cache(None)
    def _interpret_ast(ast: LazyOp) -> str:
        if (
            TernaryOps.MULACC in fxn_for_op
            and ast.op == ReduceOps.SUM
            and isinstance(ast.src[0], LazyOp)
            and ast.src[0].op == BinaryOps.MUL
        ):
            ast = LazyOp(TernaryOps.MULACC, ast.src[0].src, ast.arg)

        if ast.op is BufferOps.STORE:
            tmp = f"{gstr(fxn_for_op[ast.op], ast.op)}({_interpret_ast(ast.src[0])})"
        elif ast.op in BufferOps:
            tmp = (
                f"{gstr(fxn_for_op[ast.op], ast.op)}({gstr(ast.arg.val)}, {gstr(ast.arg.dtype)})"
                if ast.op == BufferOps.CONST
                else f"{gstr(fxn_for_op[ast.op], ast.op)}(inputs[{ast.arg.idx-1}])"
            )
            for mop, arg in ast.arg.st.to_movement_ops():
                tmp = f"{gstr(fxn_for_op[mop], mop)}({tmp}, {gstr(arg)})"
        else:
            tmp = f"{gstr(fxn_for_op[ast.op], ast.op)}({', '.join([_interpret_ast(src) for src in ast.src] + ([gstr(ast.arg)] if ast.arg else []))})"

        ret = f"a{len(lines)}"
        lines.append(f"  {ret} = {tmp}")
        return ret

    ret = _interpret_ast(ast)
    src = "\n".join(["def run(inputs, var_vals):"] + lines + [f"  return {ret}"])
    if DEBUG >= 4:
        print(
            functools.reduce(
                lambda x, y: (x.replace(y[0], str(y[1])) if y[0][0:2] == "m0" else x),
                tglob.items(),
                src,
            )
        )
    exec(compile(src, "<ast>", "exec"), tglob)  # pylint: disable=exec-used
    return InterpretedASTRunner(ast, tglob["run"])


# **************** for Compiled Devices ****************


class CompiledASTRunner(JITRunner):
    def __init__(
        self,
        ast: Optional[LazyOp],
        name: str,
        prg: str,
        global_size: Optional[List[int]] = None,
        local_size: Optional[List[int]] = None,
        runtime_args: Optional[dict] = None,
    ):
        super().__init__()
        if DEBUG >= 4:
            print(prg)
        if global_size is not None:
            global_size = global_size + [1] * (3 - len(global_size))
        if local_size is not None:
            local_size = local_size + [1] * (3 - len(local_size))
        (
            self.name,
            self.display_name,
            self.prg,
            self.global_size,
            self.local_size,
            self.runtime_args,
        ) = (
            to_function_name(name),
            name,
            prg,
            global_size,
            local_size,
            runtime_args if runtime_args is not None else {},
        )
        self.vars: List[Variable] = []
        if ast:
            info = get_lazyop_info(ast)
            self.op_estimate, self.mem_estimate = info.flops, info.mem_estimate
            from .lazy import vars_from_ast

            self.vars = vars_from_ast(ast)
            assert all(
                v._val is None for v in self.vars
            ), f"ASTRunner contains bound Variable {self.vars}"

    def build(self, compiler, runtime):
        self.lib = (
            compiler.__wrapped__(self.prg)
            if getenv("DISABLE_COMPILER_CACHE")
            else compiler(self.prg)
        )
        self.clprg = runtime(self.name, self.lib)
        return self

    def launch_dims(self, var_vals):
        global_size = (
            [sym_infer(sz, var_vals) for sz in self.global_size]
            if self.global_size is not None
            else self.global_size
        )
        local_size = (
            [sym_infer(sz, var_vals) for sz in self.local_size]
            if self.local_size is not None
            else self.local_size
        )
        return global_size, local_size

    def __call__(
        self,
        rawbufs: List[RawBuffer],
        var_vals: Dict[Variable, int],
        wait=False,
        jit=False,
    ) -> Optional[float]:
        global_size, local_size = self.launch_dims(var_vals)
        if global_size is not None and local_size is None and all_int(self.global_size):  # type: ignore[arg-type]
            # TODO: this is copied from get_program
            from .features.search import optimize_local_size

            local_size = self.local_size = optimize_local_size(
                self.clprg, global_size, rawbufs
            )
            global_size = self.global_size = [
                g // l if g % l == 0 else g / l for g, l in zip(global_size, local_size)
            ]
        lra = self.runtime_args.copy()
        if global_size:
            lra["global_size"] = global_size
        if local_size and "local_size" not in lra:
            lra["local_size"] = local_size
        et = self.clprg(
            *rawbufs, *[var_vals[k] for k in self.vars], **lra, wait=wait or DEBUG >= 2
        )
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
        buffer: Type[RawBuffer],
        linearizer_opts: LinearizerOptions,
        renderer,
        compiler,
        runtime,
        synchronize=lambda: None,
        graph=None,
    ):
        (
            self.buffer,
            self.linearizer_opts,
            self.renderer,
            self.compiler,
            self.runtime,
            self.synchronize,
            self.graph,
        ) = (buffer, linearizer_opts, renderer, compiler, runtime, synchronize, graph)

    def to_program(self, k: Linearizer) -> CompiledASTRunner:
        k.linearize()
        src, runtime_args = self.renderer(to_function_name(k.name), k.uops)
        return CompiledASTRunner(
            k.ast, k.name, src, k.global_size, k.local_size, runtime_args
        ).build(self.compiler, self.runtime)

    @functools.lru_cache(None)  # pylint: disable=method-cache-max-size-none
    def get_runner(self, ast: LazyOp) -> CompiledASTRunner:
        return self.to_program(_get_optimized_linearizer(self.linearizer_opts, ast))


def _get_optimized_linearizer(
    linearizer_opts: LinearizerOptions, ast: LazyOp
) -> Linearizer:
    if DEBUG >= 3:
        from .graph import print_tree

        print_tree(ast)
    from .codegen.linearizer import Linearizer

    k = Linearizer(ast, linearizer_opts)
    if not NOOPT:
        if not (used_tensor_cores := k.apply_tensor_cores(getenv("TC", 1))):
            k.hand_coded_optimizations()
        if BEAM >= 1:
            lins = [(("tc" if used_tensor_cores else "hc"), k)]
            if used_tensor_cores:
                lins.append(("hc", Linearizer(ast, linearizer_opts)))
                lins[-1][1].hand_coded_optimizations()
            kb = Linearizer(ast, linearizer_opts)
            from .features.search import (
                beam_search,
                time_linearizer,
                bufs_from_lin,
            )

            # TODO: this shouldn't use Device.DEFAULT, it should get the device from the LinearizerOptions
            test_rawbuffers = bufs_from_lin(
                kb
            )  # allocate scratch buffers for optimization
            lins.append(
                (
                    f"beam{BEAM.value}",
                    beam_search(
                        kb,
                        test_rawbuffers,
                        BEAM.value,
                        bool(getenv("BEAM_ESTIMATE", 1)),
                    ),
                )
            )
            timed = sorted(
                [
                    (
                        nm,
                        tk,
                        time_linearizer(
                            tk, test_rawbuffers, allow_test_size=False, clear_l2=True
                        ),
                    )
                    for nm, tk in lins
                ],
                key=lambda x: x[2],
            )
            if DEBUG >= 1:
                print(
                    "  <  ".join(
                        f"{nm:6s} : {lin.colored_shape(30, dense=True)} : {tm*1e6:8.2f} us"
                        for nm, lin, tm in timed
                    )
                )
            k = timed[0][1]
    return k
