import collections
import linecache
import math
import re
import textwrap
import typing as ta

from triton.compiler import compile as triton_compile  # type: ignore

from .. import ops
from ..codegen import uops as uo
from ..dtypes import DType
from ..dtypes import ImageDType
from ..dtypes import dtypes
from ..helpers import DEBUG
from ..helpers import getenv

triton_dtypes = {
    dtypes.double: "tl.float64",
    dtypes.float32: "tl.float32",
    dtypes.float16: "tl.float16",
    dtypes.bool: "tl.int1",
    dtypes.int8: "tl.int8",
    dtypes.uint8: "tl.uint8",
    dtypes.int32: "tl.int32",
    dtypes.int64: "tl.int64",
    dtypes.uint32: "tl.uint32",
    dtypes.uint64: "tl.uint64",
    dtypes.int16: "tl.int16",
    dtypes.uint16: "tl.uint16",
}

signature_dtypes = {
    dtypes.double: "*fp64",
    dtypes.float32: "*fp32",
    dtypes.float16: "*fp16",
    dtypes.bool: "*i8",
    dtypes.int8: "*i1",
    dtypes.uint8: "*u8",
    dtypes._arg_int32: "i32",
    dtypes.int32: "*i32",
    dtypes.int64: "*i64",
    dtypes.uint32: "*u32",
    dtypes.uint64: "*u64",
    dtypes.int16: "*i16",
    dtypes.uint16: "*u16",
}


def next_power_of_2(x):
    return 1 << (x - 1).bit_length()


def render_valid(valid):
    return '(' * (len(valid) - 1) + ') and '.join(valid) if len(valid) else 'True'


# NOTE Triton requires matching dimensions for load/store, disable this and see TestOps::test_output_padded_conv_transpose2d fail to compile
def fill_dims_for_idx(idx, dims):
    return "(" + idx + "+ (" + (f"0*({'+'.join(d for d in dims)})))") if len(dims) else idx


def get_max(var):
    if isinstance(var, int): return var
    return re.sub(r'\[(.*?)\]', '', str(var))[1:-1]


# NOTE can be removed after https://github.com/gpuocelot/gpuocelot/issues/8 gets resolved
def remove_single_scalar_curly_braces(ptx_code):
    return '\n'.join([re.sub(r'\{\s*(%\w+)\s*\}', r'\1', line) for line in ptx_code.split('\n')])


def render_const(args):
    if math.isinf(args):
        return ('-' if args < 0 else '') + 'tl.where(1,float("inf"),0)'
    if math.isnan(args):
        return 'tl.where(1,float("nan"),0)'
    return str(args)


def render_cast(x: str, dtype: DType):
    return f"{x}.to({triton_dtypes[dtype]})"


def define_scalar(local_size, dtype, args):
    if len(local_size) > 0:
        return f"tl.full(({','.join([str(next_power_of_2(x)) for x in local_size])},),{render_const(args)}, dtype={triton_dtypes[dtype]})"
    return render_const(args)


def uops_to_triton(function_name: str, uops: list[uo.UOp]):
    local_size: list[int] = []
    depth = 1
    signatures, dims, bufs, kernel, valid = [], [], [], [], []  # type: ignore

    c: ta.DefaultDict[str, int] = collections.defaultdict(int)
    r: dict[uo.UOp, str] = {}

    def ssa(u, prefix="t"):
        nonlocal c, r
        c[prefix] += 1
        r[u] = f"{prefix}{c[prefix] - 1}"
        return r[u]

    child_count: ta.DefaultDict[uo.UOp, int] = collections.defaultdict(int)
    for ru in uops:
        for v in ru.vin:
            child_count[v] += 1

    def kk(s):
        kernel.append("    " * depth + s)

    code_for_op: ta.Final[dict[ops.Op, ta.Callable]] = {
        ops.Exp2: lambda x: f"tl.math.exp2({x})",
        ops.Log2: lambda x: f"tl.math.log2({x})",
        ops.Sin: lambda x: f"tl.sin({x})",
        ops.Sqrt: lambda x: f"tl.sqrt({x})",
        ops.Neg: lambda x: f"-{x}",
        ops.Add: lambda x, y: f"({x}+{y})",
        ops.Sub: lambda x, y: f"({x}-{y})",
        ops.Mul: lambda x, y: f"({x}*{y})",
        ops.Div: lambda x, y: f"({x}/{y})" if y != '0.0' else f"{x}*tl.where({x}==0.0, float('nan'), float('inf'))",
        ops.Max2: lambda x, y: f"tl.maximum({x},{y})",
        ops.CmpLt: lambda x, y: f"({x}<{y})",
        ops.Mod: lambda x, y: f"tl.abs({x})%tl.abs({y})*tl.where({x}<0,-1,1)",
        ops.MulAcc: lambda x, y, z: f"(({x}*{y})+{z})",
        ops.Where: lambda x, y, z: f"tl.where({x},{y},{z})",
    }

    def int_div(x, y):
        return f"({x}//{y})" if y != '0' else f"{x}*tl.where({x}==0, float('nan'), float('inf'))"

    for u in uops:
        if isinstance(u, uo.Loop):
            kk(f"for {ssa(u, 'ridx')} in range({u.vin[0].arg}, {r[u.vin[1]]}):")
            depth += 1

        elif isinstance(u, uo.End):
            depth -= 1

        elif isinstance(u, uo.Alu):
            assert u.dtype is not None
            val = code_for_op[u.arg](*[r[x] for x in u.vin])
            if child_count[u] <= 1 or dtypes.is_int(u.dtype):
                r[u] = int_div(*[r[x] for x in u.vin]) if u.arg == ops.Div and dtypes.is_int(u.dtype) else val
            else:
                kk(f"{ssa(u, 'alu')} = ({val})")

        elif isinstance(u, uo.Load):
            assert u.dtype is not None
            if len(u.vin) == 2:
                kk(f"{ssa(u, 'val')} = {render_cast(f'tl.load({r[u.vin[0]]} + {fill_dims_for_idx(r[u.vin[1]], dims)}, mask = {render_valid(valid)})', u.dtype)}")
            else:
                kk(f"{ssa(u, 'val')} = {render_cast(f'tl.where({r[u.vin[2]]}, tl.load({r[u.vin[0]]}+{fill_dims_for_idx(r[u.vin[1]], dims)} , mask={render_valid(valid + [r[u.vin[2]]])}), 0.0)', u.dtype)}")

        elif isinstance(u, uo.DefineAcc):
            kk(f"{ssa(u, 'acc')} = {define_scalar(local_size, u.dtype, u.arg).replace('//', '/')}")

        elif isinstance(u, uo.Const):
            r[u] = define_scalar([], u.dtype, u.arg)

        elif isinstance(u, uo.Phi):
            kk(f"{r[u.vin[0]]} = {r[u.vin[1]].replace('//', '/')}")
            r[u] = r[u.vin[0]]

        elif isinstance(u, uo.Store):
            assert not isinstance(u.dtype, ImageDType), "unimplemented: image store"
            kk(f"tl.store({r[u.vin[0]]} + {r[u.vin[1]]}, {r[u.vin[2]].replace('//', '/')}, mask = {render_valid(valid)}) ")

        elif isinstance(u, uo.DefineGlobal):
            bufs.append(u.arg)
            signatures.append(signature_dtypes[u.arg[1]])
            r[u] = u.arg[0]

        elif isinstance(u, uo.Special):
            dims.append(u.arg[1])
            valid.append(f"{u.arg[1]}<{get_max(u.arg[2])}")
            if u.arg[1].startswith("g"):
                kk(f"{u.arg[1]} = tl.program_id({u.arg[0]}) # {u.arg[2]}")
            elif u.arg[1].startswith("l"):
                kk(f"{u.arg[1]} = tl.arange({0}, {next_power_of_2(u.arg[2])})")
                local_size.append(u.arg[2])
            r[u] = u.arg[1]

        else:
            raise TypeError(f"unimplemented: {u}")

    prg = textwrap.dedent(f"""
        import triton
        import triton.language as tl
        tl.core.TRITON_MAX_TENSOR_NUMEL = float('inf')
        @triton.jit
        def {function_name}({','.join(str(buf[0]) for buf in bufs)}):
    """)
    for i, line in enumerate(list(filter(lambda line: "tl.arange" in line, kernel))):
        kernel[kernel.index(line)] += f"[{', '.join([':' if i == j else 'None' for j in range(len(local_size))])}]"
    prg += "\n".join(kernel)

    acc_local_size = 1
    for x in local_size:
        acc_local_size *= next_power_of_2(x)
    local_size = [acc_local_size] + [1] * (len(local_size) - 1)

    if DEBUG >= 4:
        print(prg)
    getlines = linecache.getlines
    linecache.getlines = lambda filename, module_globals=None: \
        prg.splitlines(keepends=True) if "<triton>" == filename else getlines(filename, module_globals)
    exec(compile(prg, "<triton>", "exec"), globals())  # pylint: disable=W0122\
    compiled = triton_compile(
        globals()[function_name],
        signature=",".join(signatures),
        device_type="cuda",
        debug=False,
        cc=(35 if getenv("CUDACPU", 0) else None),
    )
    prg = remove_single_scalar_curly_braces(compiled.asm["ptx"].split(".file")[0].split(".visible .func")[0])
    max_local_size = [int(x) for x in prg.split(".maxntid ")[1].split("\n")[0].split(", ")]
    for i in range(len(local_size)):
        local_size[i] = min(local_size[i], max_local_size[i])
    return prg, {
        "binary": True,
        "shared": compiled.metadata["shared"],
        "local_size_override": local_size + [1] * (3 - len(local_size)),
    }
