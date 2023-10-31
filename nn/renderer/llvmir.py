import typing as ta

from llvmlite import ir  # type: ignore

from .. import ops
from ..codegen import uops as uo
from ..dtypes import dtypes


LLVM_FAST_MATH_FLAGS = ('nsz', 'arcp', 'contract', 'afn', 'reassoc')  # All from fast math, but nnan and ninf


code_for_op: ta.Final[dict[type[ops.LazyOp], ta.Callable]] = {
    ops.Neg: lambda builder, x: (
        builder.neg(x)
        if isinstance(x.type, ir.IntType) else
        builder.fneg(x, flags=LLVM_FAST_MATH_FLAGS)
    ),
    ops.Exp2: lambda builder, x: (
        builder.call(
            builder._block.module.declare_intrinsic("llvm.exp2", [ir.FloatType()]),
            [x],
            fastmath=LLVM_FAST_MATH_FLAGS,
        )
    ),
    ops.Log2: lambda builder, x: (
        builder.call(
            builder._block.module.declare_intrinsic("llvm.log2", [ir.FloatType()]),
            [x],
            fastmath=LLVM_FAST_MATH_FLAGS,
        )
    ),
    ops.Sin: lambda builder, x: (
        builder.call(
            builder._block.module.declare_intrinsic("llvm.sin", [ir.FloatType()]),
            [x],
            fastmath=LLVM_FAST_MATH_FLAGS,
        )
    ),
    ops.Sqrt: lambda builder, x: (
        builder.call(
            builder._block.module.declare_intrinsic("llvm.sqrt", [ir.FloatType()]),
            [x],
            fastmath=LLVM_FAST_MATH_FLAGS,
        )
    ),
    ops.Add: lambda builder, x, y: (
        builder.add(x, y)
        if isinstance(x.type, ir.IntType) else
        builder.fadd(x, y, flags=LLVM_FAST_MATH_FLAGS)
    ),
    ops.Sub: lambda builder, x, y: (
        builder.sub(x, y)
        if isinstance(x.type, ir.IntType) else
        builder.fsub(x, y, flags=LLVM_FAST_MATH_FLAGS)
    ),
    ops.Mul: lambda builder, x, y: (
        builder.mul(x, y)
        if isinstance(x.type, ir.IntType) else
        builder.fmul(x, y, flags=LLVM_FAST_MATH_FLAGS)
    ),
    ops.Div: lambda builder, x, y: (
        builder.sdiv(x, y)
        if isinstance(x.type, ir.IntType) else
        builder.fdiv(x, y, flags=LLVM_FAST_MATH_FLAGS)
    ),
    # TODO: this should be casted
    ops.CmpLt: lambda builder, x, y: (
        builder.zext(builder.icmp_signed("<", x, y), ir.IntType(32))
        if isinstance(x.type, ir.IntType) else
        builder.uitofp(builder.fcmp_ordered("<", x, y, flags=LLVM_FAST_MATH_FLAGS), ir.FloatType())
    ),
    ops.Max2: lambda builder, x, y: (
        builder.select(
            builder.fcmp_unordered(">", x, y, flags=LLVM_FAST_MATH_FLAGS), x, y, flags=LLVM_FAST_MATH_FLAGS
        )
    ),
    ops.Mod: lambda builder, x, y: (
        builder.srem(x, y)
    ),
    ops.MulAcc: lambda builder, x, y, z: (
        builder.fadd(
            builder.fmul(x, y, flags=LLVM_FAST_MATH_FLAGS), z, flags=LLVM_FAST_MATH_FLAGS
        )
    ),
    ops.Where: lambda builder, x, y, z: (
        builder.select(
            builder.fcmp_unordered("!=", x, ir.Constant(ir.FloatType(), 0), flags=LLVM_FAST_MATH_FLAGS)
            if isinstance(x.type, ir.FloatType) else
            builder.trunc(x, ir.IntType(1)),
            y,
            z,
            flags=LLVM_FAST_MATH_FLAGS,
        )
    ),
}

dtype_to_llvm_dtype = {
    dtypes.float64: ir.DoubleType(),
    dtypes.float16: ir.HalfType(),
    dtypes.bfloat16: ir.IntType(16),
    dtypes.float32: ir.FloatType(),
    dtypes.int8: ir.IntType(8),
    dtypes.uint8: ir.IntType(8),
    dtypes.bool: ir.IntType(1),
    dtypes.int64: ir.IntType(64),
    dtypes.int32: ir.IntType(32),
    dtypes._arg_int32: ir.IntType(32),
}


def cast(bb, val, input_type, output_type):
    if input_type == output_type:
        return val

    if output_type == dtypes.float32:
        if dtypes.is_int(input_type) or input_type == dtypes.bool:
            val = (
                bb[-1].uitofp(val, ir.FloatType())
                if dtypes.is_unsigned(input_type) or input_type == dtypes.bool
                else bb[-1].sitofp(val, ir.FloatType())
            )
        elif input_type == dtypes.bfloat16:
            val = bb[-1].sext(val, ir.IntType(32))
            val = bb[-1].shl(val, ir.Constant(ir.IntType(32), 16))
            val = bb[-1].bitcast(val, ir.FloatType())
        elif input_type == dtypes.float64:
            val = bb[-1].fptrunc(val, ir.FloatType())
        else:
            val = bb[-1].fpext(val, ir.FloatType())
        return val

    if input_type == dtypes.float32:
        if dtypes.is_int(output_type) or output_type == dtypes.bool:
            if dtypes.is_unsigned(output_type):
                val = bb[-1].fptoui(val, dtype_to_llvm_dtype[output_type])
            elif output_type == dtypes.bool:
                val = bb[-1].fcmp_ordered("!=", val, ir.Constant(ir.FloatType(), 0), flags=LLVM_FAST_MATH_FLAGS)
            else:
                val = bb[-1].fptosi(val, dtype_to_llvm_dtype[output_type])
        elif output_type == dtypes.bfloat16:
            val = bb[-1].bitcast(val, ir.IntType(32))
            val = bb[-1].lshr(val, ir.Constant(ir.IntType(32), 16))
            val = bb[-1].trunc(val, ir.IntType(16))
        elif output_type == dtypes.float64:
            val = bb[-1].fpext(val, ir.DoubleType())
        else:
            val = bb[-1].fptrunc(val, dtype_to_llvm_dtype[output_type])
        return val

    raise NotImplementedError(
        f"cast from {input_type} -> {output_type} not implemented"
    )


def uops_to_llvm_ir(function_name: str, uops: list[uo.UOp]) -> tuple[str, dict]:
    # all llvm stuff goes into a module
    module = ir.Module(name=__file__)

    # extract global buffers
    buf_to_dtype = {
        u.arg[0]: u.arg[1] for u in uops if isinstance(u, uo.DefineGlobal)
    }
    buf_index = {x: i for i, x in enumerate(buf_to_dtype.keys())}

    # create llvm function
    func_dtypes = [
        (dtype_to_llvm_dtype[dtype], dtype) for dtype in buf_to_dtype.values()
    ]
    func = ir.Function(
        module,
        ir.FunctionType(
            ir.VoidType(),
            [x.as_pointer() if dt != dtypes._arg_int32 else x for x, dt in func_dtypes],
        ),
        name=function_name,
    )
    for a in func.args:
        if a.type.is_pointer:
            a.add_attribute("noalias")

    # force llvmlite to allow us to add function attribute then add the attribute
    func.attributes._known = func.attributes._known.union(
        frozenset(['"no-nans-fp-math"="true"'])
    )
    func.attributes.add('"no-nans-fp-math"="true"')

    bb = [ir.IRBuilder(func.append_basic_block("entry"))]
    loop_blocks: list = []
    reduce_phis: list = []
    # TODO: newvar probably shouldn't be optional
    lvars: dict[ta.Optional[uo.UOp], ta.Any] = {}  # this Any is an llvm type

    for bufname, dtype in buf_to_dtype.items():
        if dtype == dtypes._arg_int32:
            lvars[bufname] = bb[-1].sext(func.args[buf_index[bufname]], ir.IntType(32))

    for u in uops:
        if isinstance(u, uo.Loop):
            bb.append(
                ir.IRBuilder(func.append_basic_block(f"loop_body_{len(loop_blocks)}"))
            )
            bb[-2].branch(bb[-1]._block)

            phis = []
            for rp in reduce_phis:
                incoming = lvars[rp]
                lvars[rp] = bb[-1].phi(ir.FloatType())
                lvars[rp].add_incoming(incoming, bb[-2]._block)
                phis.append((rp, lvars[rp]))

            lvars[u] = bb[-1].phi(ir.IntType(32), name=f"loop{len(loop_blocks)}")
            lvars[u].add_incoming(lvars[u.vin[0]], bb[-2]._block)
            loop_blocks.append((bb[-1], phis))

        elif isinstance(u, uo.End):
            block, phis = loop_blocks.pop()
            idx_p1 = bb[-1].add(lvars[u.vin[0]], ir.Constant(ir.IntType(32), 1))
            lvars[u.vin[0]].add_incoming(idx_p1, bb[-1]._block)
            for n, phi in phis:
                phi.add_incoming(lvars[n], bb[-1]._block)
            bb.append(
                ir.IRBuilder(func.append_basic_block(f"loop_exit_{len(loop_blocks)}"))
            )
            bb[-2].cbranch(
                bb[-2].icmp_unsigned("<", idx_p1, lvars[u.vin[0].vin[1]]),
                block._block,
                bb[-1]._block,
            )

        elif isinstance(u, uo.DefineGlobal):
            lvars[u] = func.args[buf_index[u.arg[0]]]

        elif isinstance(u, uo.DefineAcc):
            lvars[u] = ir.Constant(dtype_to_llvm_dtype[u.dtype], u.arg)
            reduce_phis.append(u)

        elif isinstance(u, uo.Special):
            lvars[u] = lvars[u.arg.expr]

        elif isinstance(u, uo.Const):
            value = (
                int(u.arg)
                if dtypes.is_int(u.dtype)
                else bool(u.arg)
                if u.dtype == dtypes.bool
                else u.arg
            )
            lvars[u] = ir.Constant(dtype_to_llvm_dtype[u.dtype], value)

        elif isinstance(u, uo.Load):
            assert u.dtype is not None
            if len(u.vin) > 2:
                gate = bb[-1].trunc(lvars[u.vin[2]], ir.IntType(1))
                aug_idx = bb[-1].select(
                    gate, lvars[u.vin[1]], ir.Constant(ir.IntType(32), 0)
                )
                val = bb[-1].load(bb[-1].gep(lvars[u.vin[0]], [aug_idx], inbounds=True))
                val = cast(bb, val, u.vin[0].dtype, u.dtype)
                val = bb[-1].select(gate, val, lvars[u.vin[3]])
            else:
                val = bb[-1].load(
                    bb[-1].gep(lvars[u.vin[0]], [lvars[u.vin[1]]], inbounds=True)
                )
                val = cast(bb, val, u.vin[0].dtype, u.dtype)
            lvars[u] = val

        elif isinstance(u, uo.Phi):
            lvars[u] = lvars[u.vin[1]]
            # PHI UOps can link to other PHI Uops, backtrace this to DEFINE_ACC
            backward = u.vin[0]
            while isinstance(backward, uo.Phi):
                backward = backward.vin[0]
            lvars[backward] = lvars[u]

        elif isinstance(u, uo.Store):
            element = cast(bb, lvars[u.vin[2]], u.vin[2].dtype, u.vin[0].dtype)
            bb[-1].store(element, bb[-1].gep(lvars[u.vin[0]], [lvars[u.vin[1]]], inbounds=True))

        elif isinstance(u, uo.Alu):
            lvars[u] = code_for_op[u.arg](bb[-1], *[lvars[x] for x in u.vin])

    bb[-1].ret_void()
    return str(module), {"binary":False}
