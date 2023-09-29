import collections
import math
import typing as ta

from ..codegen.linearizer import UOp
from ..codegen.linearizer import UOps
from ..dtypes import DType
from ..dtypes import ImageDType
from ..dtypes import dtypes
from ..helpers import prod
from ..helpers import strip_parens
from ..ops import BinaryOps
from ..ops import TernaryOps
from ..ops import UnaryOps


class CStyleLanguage(ta.NamedTuple):
    size_prefix: str = "int"
    generic_var_prefix: str = ""
    kernel_prefix: str = ""
    buffer_prefix: str = ""
    buffer_suffix: str = ""
    smem_prefix: str = ""
    arg_int_prefix: str = ""
    barrier: str = ""
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
        UnaryOps.NEG: lambda x: f"(-{x})",
        UnaryOps.EXP2: lambda x: f"exp2({x})",
        UnaryOps.LOG2: lambda x: f"log2({x})",
        UnaryOps.SIN: lambda x: f"sin({x})",
        UnaryOps.SQRT: lambda x: f"sqrt({x})",
        BinaryOps.ADD: lambda a, b: f"({a}+{b})",
        BinaryOps.SUB: lambda a, b: f"({a}-{b})",
        BinaryOps.MUL: lambda a, b: f"({a}*{b})",
        BinaryOps.DIV: lambda a, b: f"({a}/{b})",
        BinaryOps.MAX: lambda a, b: f"max({a},{b})",
        BinaryOps.MOD: lambda a, b: f"({a}%{b})",
        BinaryOps.CMPLT: lambda a, b: f"({a}<{b})",
        TernaryOps.MULACC: lambda a, b, c: f"(({a}*{b})+{c})",
        TernaryOps.WHERE: lambda a, b, c: f"({a}!=0?{b}:{c})",
    }

    # returns a str expression of the casted xs with the given type
    def render_cast(self, x: list[str], var_dtype: DType) -> str:
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
        cast = f"({output_dtype.name})" if output_dtype != buf_dtype else ""
        if output_dtype.sz > 1:
            return f"{cast}(*(({self.smem_prefix if local else self.buffer_prefix}{buf_dtype.name}{output_dtype.sz}*)({buf_name}+{idx})))"
        return (
            f"{cast}(*({buf_name}+{idx}))"
            if self.uses_ptr_arithmetic
            else f"{cast}({buf_name}[{idx}])"
        )

    def render_local(self, name: str, size: int):
        return self.smem_prefix + f"float {name}[{size}];"

    def render_for(
        self, expr: str, _min: ta.Union[int, str], _max: ta.Union[int, str]
    ) -> str:
        return f"for (int {expr} = {_min}; {expr} <= {_max}; ++{expr}) {{"

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
                f"{self.kernel_prefix}void {f'__launch_bounds__ ({prod(local_size)}, 1) ' if self.launch_bounds else ''}{function_name}(",
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
            return f"*(({self.smem_prefix if local else self.buffer_prefix}{buf_dtype.name}{var_dtype.sz}*)({buf_name}+{idx})) = ({buf_dtype.name}{var_dtype.sz}){var_name};"
        return (
            f"*({buf_name}+{idx}) = {var_name};"
            if self.uses_ptr_arithmetic
            else f"{buf_name}[{idx}] = {var_name};"
        )


def uops_to_cstyle(lang: CStyleLanguage, function_name: str, uops: list[UOp]) -> str:
    local_size: list[int] = []
    kernel, prekernel, bufs = [], [], []
    # pend_close = None
    depth = 1

    def kk(s):
        kernel.append("  " * depth + s)

    c: ta.DefaultDict[str, int] = collections.defaultdict(int)
    r: dict[UOp, str] = {}

    def ssa(u, prefix="t"):
        nonlocal c, r
        c[prefix] += 1
        r[u] = f"{prefix}{c[prefix]-1}"
        return r[u]

    child_count: ta.DefaultDict[UOp, int] = collections.defaultdict(int)
    for ru in uops:
        for v in ru.vin:
            child_count[v] += 1

    for u in uops:
        uop, dtype, vin, args, _ = u
        if uop == UOps.LOOP:
            kk(lang.render_for(ssa(u, "ridx"), r[vin[0]], r[vin[1]]))
            depth += 1
        elif uop == UOps.BARRIER:
            kk(lang.barrier)
        elif uop == UOps.END:
            depth -= 1
            kk("}")
        elif uop == UOps.WMMA:
            if args == "METAL":
                # ((lidx2*32)+(lidx3*4)+(lidx4*16)+(lidx5*8)+(lidx6*2))
                kk("{ simdgroup_float8x8 a,b,c;")
                kk(
                    f"a.thread_elements()[0] = {r[vin[0]]}; a.thread_elements()[1] = {r[vin[1]]};"
                )
                kk(
                    f"b.thread_elements()[0] = {r[vin[2]]}; b.thread_elements()[1] = {r[vin[3]]};"
                )
                kk(
                    f"c.thread_elements()[0] = {r[vin[4]]}; c.thread_elements()[1] = {r[vin[5]]};"
                )
                kk("simdgroup_multiply_accumulate(c, a, b, c);")
                kk(
                    f"{r[vin[4]]} = c.thread_elements()[0]; {r[vin[5]]} = c.thread_elements()[1]; }}"
                )
            elif args == "HIP":
                kk("{")
                kk(
                    f"half16 a_frag = {{ {','.join(['(half)'+r[x] for x in vin[8:8+16]])} }};"
                )
                kk(
                    f"half16 b_frag = {{ {','.join(['(half)'+r[x] for x in vin[8+16:8+32]])} }};"
                )
                kk(f"float8 c_frag = {{ {','.join([r[x] for x in vin[:8]])} }};")
                kk(
                    "c_frag = __builtin_amdgcn_wmma_f32_16x16x16_f16_w32(a_frag, b_frag, c_frag);"
                )
                for i in range(8):
                    kk(f"{r[vin[i]]} = c_frag[{i}];")
                kk("}")
            else:
                raise NotImplementedError(f"WMMA not implemented for {args}")
        elif uop == UOps.ALU:
            assert dtype is not None
            # remove parens if ALU types are the same. TODO: can do more here
            if (
                vin[0].uop == UOps.ALU
                and vin[0].arg == args
                and args in {BinaryOps.ADD, BinaryOps.SUB, BinaryOps.MUL}
            ):
                val = lang.code_for_op[args](
                    strip_parens(r[vin[0]]), *[r[x] for x in vin[1:]]
                )
            else:
                val = lang.code_for_op[args](*[r[x] for x in vin])
            assert child_count[u] != 0, f"childless ALU op found {u}"
            if child_count[u] <= 1 or dtypes.is_int(dtype):  # fix index rendering issue
                r[u] = val
            else:
                kk(
                    f"{lang.generic_var_prefix if lang.generic_var_prefix else dtype.name} {ssa(u,'alu')} = {val};"
                )
        elif uop == UOps.DEFINE_ACC:
            assert dtype is not None
            kk(
                f"{lang.generic_var_prefix if lang.generic_var_prefix else dtype.name} {ssa(u,'acc')} = {lang.render_const(args, dtype)};"
            )
        elif uop == UOps.SPECIAL:
            xid = lang.gid if args[1].startswith("g") else lang.lid
            kk(f"{lang.size_prefix} {args[1]} = {xid[args[0]]}; /* {args[2]} */")
            if args[1].startswith("l"):
                local_size.append(args[2])
            r[u] = args[1]
        elif uop == UOps.CONST:
            r[u] = (
                lang.render_const(args, dtype)
                if args >= 0
                else f"({lang.render_const(args, dtype)})"
            )
        elif uop == UOps.LOAD:
            assert dtype is not None
            val = lang.render_load(
                dtype,
                r[vin[0]],
                vin[0].dtype,
                strip_parens(r[vin[1]]),
                vin[0].uop == UOps.DEFINE_LOCAL,
            )
            if len(vin) > 2:
                val = lang.render_conditional(r[vin[2]], val, r[vin[3]])
            kk(
                f"{lang.generic_var_prefix if lang.generic_var_prefix else dtype.name} {ssa(u,'val')} = {val};"
            )
        elif uop == UOps.STORE:
            if len(vin) == 2:
                kk(f"{r[vin[0]]} = {r[vin[1]]};")
            elif len(vin) == 3:
                assert vin[0].dtype is not None and vin[2].dtype is not None
                kk(
                    lang.render_store(
                        r[vin[0]],
                        vin[0].dtype,
                        r[vin[2]],
                        vin[2].dtype,
                        strip_parens(r[vin[1]]),
                        vin[0].uop == UOps.DEFINE_LOCAL,
                    )
                )
        elif uop == UOps.CAST and dtype is not None and dtype.sz > 1:
            val = lang.render_cast([r[x] for x in vin], dtype)
            if child_count[u] <= 1:
                r[u] = val
            else:
                kk(
                    f"{lang.generic_var_prefix if lang.generic_var_prefix else dtype.name} {ssa(u,'cast')} = {val};"
                )
        elif uop == UOps.DEFINE_LOCAL:
            if lang.external_local_bufs:
                prekernel.append(lang.render_local(args[0], args[1]))
            else:
                kk(lang.render_local(args[0], args[1]))
            r[u] = args[0]
        elif uop == UOps.DEFINE_GLOBAL:
            bufs.append(args)
            r[u] = args[0]
        elif uop == UOps.GEP:
            r[u] = f"({r[vin[0]]}).{'xyzw'[args]}"
        else:
            raise RuntimeError(f"failed to render {uop}")

    return lang.render_kernel(function_name, kernel, bufs, local_size, prekernel)
