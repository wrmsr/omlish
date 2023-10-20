import collections
import math
import typing as ta

from .. import ops
from ..codegen import uops as uo
from ..dtypes import DType
from ..dtypes import ImageDType
from ..dtypes import dtypes
from ..helpers import prod
from ..helpers import strip_parens


class CStyleLanguage(ta.NamedTuple):
    size_prefix: str = "int"
    generic_var_prefix: str = ""
    kernel_prefix: str = ""
    buffer_prefix: str = ""
    buffer_suffix: str = ""
    smem_align: str = ""
    smem_prefix: str = ""
    smem_prefix_for_cast: bool = True
    arg_int_prefix: str = ""
    barrier: str = ""
    xid: list[str] = []
    gid: list[str] = []
    lid: list[str] = []
    global_max: list[int] = []
    local_max: list[int] = []
    extra_args: list[str] = []
    float4: ta.Optional[str] = None
    half_prekernel: ta.Optional[str] = None
    uses_vload: bool = False
    external_local_bufs: bool = False
    uses_ptr_arithmetic: bool = False
    launch_bounds: bool = False
    code_for_op: dict = {
        ops.Neg: lambda x: f"(-{x})",
        ops.Exp2: lambda x: f"exp2({x})",
        ops.Log2: lambda x: f"log2({x})",
        ops.Sin: lambda x: f"sin({x})",
        ops.Sqrt: lambda x: f"sqrt({x})",
        ops.Add: lambda a, b: f"({a}+{b})",
        ops.Sub: lambda a, b: f"({a}-{b})",
        ops.Mul: lambda a, b: f"({a}*{b})",
        ops.Div: lambda a, b: f"({a}/{b})",
        ops.Max2: lambda a, b: f"max({a},{b})",
        ops.Mod: lambda a, b: f"({a}%{b})",
        ops.CmpLt: lambda a, b: f"({a}<{b})",
        ops.MulAcc: lambda a, b, c: f"(({a}*{b})+{c})",
        ops.Where: lambda a, b, c: f"({a}!=0?{b}:{c})",
    }

    # returns a str expression of the casted xs with the given type
    def render_cast(self, x: list[str], var_dtype: DType) -> str:
        if len(x) == 1:
            return f"({var_dtype.name})({x[0]})"
        assert len(x) == var_dtype.sz, f"cast is wrong size {len(x)} != {var_dtype.sz}"
        assert self.float4 is not None, "cast is not supported on this platform"
        if var_dtype == dtypes._float4:
            return f"{self.float4}({','.join(x)})"
        if var_dtype == dtypes._float2:
            return f"{self.float4.replace('float4', 'float2')}({','.join(x)})"
        if var_dtype == dtypes._int2:
            return f"{self.float4.replace('float4', 'int2')}({','.join(x)})"
        raise NotImplementedError(f"no cast for {var_dtype}")

    # returns a str expression of the const with the given type
    def render_const(self, x: ta.Union[float, int], var_dtype) -> str:
        if math.isnan(x):
            val = "NAN"
        elif math.isinf(x):
            val = ("-" if x < 0 else "") + "INFINITY"
        else:
            val = (
                f"{x}f"
                if dtypes.is_float(var_dtype) and isinstance(x, float)
                else f"{int(x)}"
            )
        return (
            self.render_cast([val] * var_dtype.sz, var_dtype)
            if var_dtype.sz > 1
            else val
        )

    # returns a str expression of the loaded value with the output type
    def render_load(self, output_dtype, buf_name, buf_dtype, idx, local=False) -> str:
        if isinstance(buf_dtype, ImageDType):
            assert output_dtype == dtypes._float4, "images must be float4"
            return f"read_imagef({buf_name}, smp, {idx})"
        if self.uses_vload and buf_dtype == dtypes.float16:
            return f"vload_half{'' if output_dtype.sz == 1 else str(output_dtype.sz)}(0, {buf_name}+{idx})"
        if output_dtype.sz > 1:
            out_val = f"*(({self.smem_prefix if local and self.smem_prefix_for_cast else self.buffer_prefix}{buf_dtype.name}{output_dtype.sz}*)({buf_name}+{idx}))"
        else:
            out_val = f"*({buf_name}+{idx})" if self.uses_ptr_arithmetic else f"{buf_name}[{idx}]"

        return self.render_cast([out_val], output_dtype) if output_dtype != buf_dtype else out_val

    def render_local(self, name:str, size:int):
        return self.smem_align + self.smem_prefix + f"float {name}[{size}];"

    def render_for(
        self, expr: str, _min: ta.Union[int, str], _max: ta.Union[int, str]
    ) -> str:
        return f"for (int {expr} = {_min}; {expr} < {_max}; ++{expr}) {{"

    def render_if(self, cond: str):
        return f"if ({cond}) {{"

    def render_conditional(self, cond: str, x: str, y: str) -> str:
        return f"({cond})?({x}):{y}"

    def render_kernel(
        self,
        function_name: str,
        kernel: list[str],
        bufs: list[tuple[str, DType]],
        local_size: list[int],
        prekernel: list[str],
    ) -> str:
        tmp = (
            "const sampler_t smp = CLK_NORMALIZED_COORDS_FALSE | CLK_ADDRESS_CLAMP | CLK_FILTER_NEAREST;\n"
            if any(isinstance(dtype, ImageDType) for _, dtype in bufs)
            else ""
        )
        buftypes = [
            (
                name,
                f"{'read_only' if i > 0 else 'write_only'} image2d_t"
                if dtype.name.startswith("image")
                else self.arg_int_prefix
                if dtype == dtypes._arg_int32
                else ("const " if i > 0 else "")
                + self.buffer_prefix
                + dtype.name
                + "*"
                + self.buffer_suffix,
            )
            for i, (name, dtype) in enumerate(bufs)
        ]
        prg = "".join(
            [
                f"{self.kernel_prefix}void "
                f"{f'__launch_bounds__ ({prod(local_size)}, 1) ' if self.launch_bounds else ''}{function_name}(",
            ]
            + [", ".join([f"{t} {name}" for name, t in buftypes] + self.extra_args)]
            + [") {\n" + tmp]
            + ["\n".join(kernel), "\n}"]
        )
        if self.half_prekernel and any(dtype == dtypes.float16 for _, dtype in bufs):
            prg = "".join([f"{self.half_prekernel}", "\n", prg])
        return prg

    # returns a str statement that does the store
    def render_store(
        self,
        buf_name: str,
        buf_dtype: DType,
        var_name: str,
        var_dtype: DType,
        idx: str,
        local=False,
    ) -> str:
        if isinstance(buf_dtype, ImageDType):
            assert var_dtype == dtypes._float4, "images must be float4"
            return f"write_imagef({buf_name}, {idx}, {var_name});"
        if self.uses_vload and buf_dtype == dtypes.float16:
            return f"vstore_half{'' if var_dtype.sz == 1 else str(var_dtype.sz)}({var_name}, 0, {buf_name}+{idx});"
        if var_dtype.sz > 1:
            return f"*(({self.smem_prefix if local and self.smem_prefix_for_cast else self.buffer_prefix}{buf_dtype.name}{var_dtype.sz}*)({buf_name}+{idx})) = ({buf_dtype.name}{var_dtype.sz}){var_name};"
        return (
            f"*({buf_name}+{idx}) = {var_name};"
            if self.uses_ptr_arithmetic
            else f"{buf_name}[{idx}] = {var_name};"
        )


def uops_to_cstyle(lang: CStyleLanguage, function_name: str, uops: list[uo.UOp]) -> tuple[str, dict]:
    local_size: list[int] = []
    kernel, prekernel, bufs = [], [], []
    # pend_close = None
    depth = 1

    def kk(s):
        kernel.append("  " * depth + s)

    c: ta.DefaultDict[str, int] = collections.defaultdict(int)
    r: dict[uo.UOp, str] = {}

    def ssa(u, prefix="t"):
        nonlocal c, r
        c[prefix] += 1
        r[u] = f"{prefix}{c[prefix]-1}"
        return r[u]

    child_count: ta.DefaultDict[uo.UOp, int] = collections.defaultdict(int)
    for ru in uops:
        for v in ru.vin:
            child_count[v] += 1

    for u in uops:
        if isinstance(u, uo.Loop):
            kk(lang.render_for(ssa(u, "ridx"), r[u.vin[0]], r[u.vin[1]]))
            depth += 1

        elif isinstance(u, uo.If):
            kk(lang.render_if(r[u.vin[0]]))
            depth += 1

        elif isinstance(u, uo.Barrier):
            kk(lang.barrier)

        elif isinstance(u, uo.End):
            depth -= 1
            kk("}")

        elif isinstance(u, uo.Wmma):
            if u.arg[0] == "METAL":
                # ((lidx2*32)+(lidx3*4)+(lidx4*16)+(lidx5*8)+(lidx6*2))
                kk("{ simdgroup_float8x8 a,b,c;")
                kk(f"a.thread_elements()[0] = {r[u.vin[0]]}; a.thread_elements()[1] = {r[u.vin[1]]};")
                kk(f"b.thread_elements()[0] = {r[u.vin[2]]}; b.thread_elements()[1] = {r[u.vin[3]]};")
                kk(f"c.thread_elements()[0] = {r[u.vin[4]]}; c.thread_elements()[1] = {r[u.vin[5]]};")
                kk("simdgroup_multiply_accumulate(c, a, b, c);")
                kk(f"{r[u.vin[4]]} = c.thread_elements()[0]; {r[u.vin[5]]} = c.thread_elements()[1]; }}")

            elif u.arg[0] == "HIP":
                kk("{")
                kk(f"half16 a_frag = {{ {','.join(['(half)'+r[x] for x in u.vin[0:16]])} }};")
                kk(f"half16 b_frag = {{ {','.join(['(half)'+r[x] for x in u.vin[16:32]])} }};")
                kk(f"float8 c_frag = {{ {','.join([r[x] for x in u.vin[32:]])} }};")
                kk("c_frag = __builtin_amdgcn_wmma_f32_16x16x16_f16_w32(a_frag, b_frag, c_frag);")
                for i in range(8):
                    kk(f"{r[u.vin[32+i]]} = c_frag[{i}];")
                kk("}")

            else:
                raise NotImplementedError(f"WMMA not implemented for {u.arg}")

        elif isinstance(u, uo.Alu):
            assert u.dtype is not None
            # remove parens if ALU types are the same. TODO: can do more here
            if (
                isinstance(u.vin[0], uo.Alu)
                and u.vin[0].arg == u.arg
                and u.arg in {ops.Add, ops.Sub, ops.Mul}
            ):
                val = lang.code_for_op[u.arg](
                    strip_parens(r[u.vin[0]]), *[r[x] for x in u.vin[1:]]
                )
            else:
                val = lang.code_for_op[u.arg](*[r[x] for x in u.vin])
            assert child_count[u] != 0, f"childless ALU op found {u}"
            if child_count[u] <= 1 or dtypes.is_int(u.dtype):  # fix index rendering issue
                r[u] = val
            else:
                kk(
                    f"{lang.generic_var_prefix if lang.generic_var_prefix else u.dtype.name} {ssa(u,'alu')} = {val};"
                )

        elif isinstance(u, uo.DefineAcc):
            assert u.dtype is not None
            kk(
                f"{lang.generic_var_prefix if lang.generic_var_prefix else u.dtype.name} "
                f"{ssa(u,'acc')} = {lang.render_const(u.arg, u.dtype)};"
            )

        elif isinstance(u, uo.Special):
            xid = lang.gid if u.arg[1].startswith("g") else (lang.xid if u.arg[1].startswith("i") else lang.lid)
            kk(f"{lang.size_prefix} {u.arg[1]} = {xid[u.arg[0]]}; /* {u.arg[2]} */")
            if u.arg[1].startswith("l"):
                local_size.append(u.arg[2])
            r[u] = u.arg[1]

        elif isinstance(u, uo.Const):
            r[u] = (
                lang.render_const(u.arg, u.dtype)
                if u.arg >= 0
                else f"({lang.render_const(u.arg, u.dtype)})"
            )

        elif isinstance(u, uo.Load):
            assert u.dtype is not None
            val = lang.render_load(
                u.dtype,
                r[u.vin[0]],
                u.vin[0].dtype,
                strip_parens(r[u.vin[1]]),
                isinstance(u.vin[0], uo.DefineLocal),
            )
            if len(u.vin) > 2:
                val = lang.render_conditional(r[u.vin[2]], val, r[u.vin[3]])
            kk(
                f"{lang.generic_var_prefix if lang.generic_var_prefix else u.dtype.name} {ssa(u,'val')} = {val};"
            )

        elif isinstance(u, uo.Phi):
            kk(f"{r[u.vin[0]]} = {r[u.vin[1]]};")
            r[u] = r[u.vin[0]]

        elif isinstance(u, uo.Store):
            assert u.vin[0].dtype is not None and u.vin[2].dtype is not None
            kk(
                lang.render_store(
                    r[u.vin[0]],
                    u.vin[0].dtype,
                    r[u.vin[2]],
                    u.vin[2].dtype,
                    strip_parens(r[u.vin[1]]),
                    isinstance(u.vin[0], uo.DefineLocal),
                ),
            )

        elif isinstance(u, uo.Cast) and u.dtype is not None and u.dtype.sz > 1:
            val = lang.render_cast([r[x] for x in u.vin], u.dtype)
            if child_count[u] <= 1:
                r[u] = val
            else:
                kk(
                    f"{lang.generic_var_prefix if lang.generic_var_prefix else u.dtype.name} "
                    f"{ssa(u,'cast')} = {val};"
                )

        elif isinstance(u, uo.DefineLocal):
            if lang.external_local_bufs:
                prekernel.append(lang.render_local(u.arg[0], u.arg[1]))
            else:
                kk(lang.render_local(u.arg[0], u.arg[1]))
            r[u] = u.arg[0]

        elif isinstance(u, uo.DefineGlobal):
            bufs.append(u.arg)
            r[u] = u.arg[0]

        elif isinstance(u, uo.Gep):
            r[u] = f"({r[u.vin[0]]}).{'xyzw'[u.arg]}"

        else:
            raise RuntimeError(f"failed to render {type(u).__name__}")

    return lang.render_kernel(function_name, kernel, bufs, local_size, prekernel), {"binary":False}
