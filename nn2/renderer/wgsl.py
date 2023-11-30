import typing as ta
import math

from .. import ops
from ..dtypes import DType
from ..dtypes import dtypes
from ..renderer.cstyle import CStyleLanguage


type_map = {
    dtypes.float: "f32",
    dtypes.half: "f16",
    dtypes.int32: "i32",
    dtypes.uint32: "u32",
    dtypes.bool: "bool",
}


class WgslLanguage(CStyleLanguage):
    gid = [f"i32(gindex.{'xyz'[x]})" for x in range(3)]
    lid = [f"i32(lindex.{'xyz'[x]})" for x in range(3)]
    size_prefix = "let"
    barrier = "workgroupBarrier();"
    generic_var_prefix = "var "
    external_local_bufs = True
    code_for_op = {
        ops.Neg: lambda x: f"(-{x})",
        ops.Exp2: lambda x: f"exp2({x})",
        ops.Log2: lambda x: f"log2({x})",
        ops.Sin: lambda x: f"sin({x})",
        ops.Sqrt: lambda x: f"sqrt({x})",
        ops.Add: lambda x, y: f"({x}+{y})",
        ops.Sub: lambda x, y: f"({x}-{y})",
        ops.Mul: lambda x, y: f"({x}*{y})",
        ops.Div: lambda x, y: f"({x}/{y})",
        ops.Mod: lambda x, y: f"({x}%{y})",
        ops.Max2: lambda x, y: f"max({x},{y})",
        ops.CmpLt: lambda x, y: f"f32({x}<{y})",
        ops.MulAcc: lambda x, y, z: f"fma({x},{y},{z})",
        ops.Where: lambda a, b, c: f"select({c},{b},{a}!=0.)",
    }

    def render_local(self, name: str, size: int):
        return f"var<workgroup> {name}: array<f32,{size}>;"

    def render_const(self, x: ta.Union[float, int], var_dtype) -> str:
        if math.isnan(x):
            val = "nan()"
        elif math.isinf(x):
            val = ("-" if x < 0 else "") + "0x1.fffffep+127f"
        else:
            val = f"({x}" + ("" if dtypes.is_int(var_dtype) else "f") + ")"
        return (
            self.render_cast([val] * var_dtype.sz, var_dtype)
            if var_dtype.sz > 1
            else val
        )

    def render_kernel(
        self,
        function_name: str,
        kernel: list[str],
        bufs: list[tuple[str, DType]],
        local_size: list[int],
        prekernel: list[str],
    ) -> str:
        local_size = local_size[::-1] if local_size else [1]
        bind_it = iter(range(len(bufs)))
        prg = "fn nan() -> f32 { let bits = 0xffffffffu; return bitcast<f32>(bits); }\n"
        prg += "\n".join(
            prekernel
            + [
                f"@group(0) @binding({next(bind_it)}) var<storage,read_write> {name}: array<{type_map[dtype]}>;"
                for name, dtype in bufs
            ]
        )
        prg += (
            f"\n@compute @workgroup_size({','.join([str(x) for x in local_size])}) "
            f"fn {function_name}"
            f"(@builtin(workgroup_id) gindex: vec3<u32>, @builtin(local_invocation_id) lindex: vec3<u32>) {{\n"
            + "\n".join(kernel)
            + "\n}"
        )
        return prg

    def render_for(
        self, expr: str, _min: ta.Union[int, str], _max: ta.Union[int, str]
    ) -> str:
        return f"for(var {expr} = {_min}; {expr} < {_max}; {expr}++) {{"

    def render_if(self, cond: str):
        return f"if (bool({cond})) {{"

    def render_conditional(self, cond: str, x: str, y: str) -> str:
        return f"select(f32({y}), {x}, bool({cond}))"

    def render_cast(self, x: list[str], var_dtype: DType) -> str:
        if type_map[var_dtype]:
            return f"{type_map[var_dtype]}({x[0]})"
        raise TypeError(f"no cast for {var_dtype}")

    def render_load(self, output_dtype, buf_name, buf_dtype, idx, local=False) -> str:
        return (
            f"f32({super().render_load(output_dtype, buf_name, buf_dtype, idx, local)})"
        )

    def render_store(
        self,
        buf_name: str,
        buf_dtype: DType,
        var_name: str,
        var_dtype: DType,
        idx,
        local=False,
    ) -> str:
        if buf_dtype != var_dtype:
            var_name = f"{type_map[buf_dtype]}({var_name})"
        return f"{buf_name}[{idx}] = {var_name};"
