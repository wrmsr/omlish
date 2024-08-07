import functools
import re
import typing as ta

from .. import ops
from ..helpers import DEBUG
from ..runtime.lib import RawBuffer
from ..shape.symbolic import Variable


def interpret_ast(
        fxn_for_op: dict[type[ops.LazyOp], ta.Callable],
        from_underlying: ta.Optional[ta.Callable],
        ast: ops.LazyOp,
) -> ta.Callable[[list[RawBuffer], dict[Variable, int]], RawBuffer]:
    if DEBUG >= 3:
        from ..lazy import print_tree
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
    def _interpret_ast(ast: ops.LazyOp) -> str:
        if (
                ops.MulAcc in fxn_for_op
                and isinstance(ast, ops.Sum)
                and isinstance(ast.src[0], ops.LazyOp)
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
            functools.reduce(
                lambda x, y: (x.replace(y[0], str(y[1])) if y[0][0:2] == "m0" else x),
                tglob.items(),
                src,
            ),
        )

    exec(compile(src, "<ast>", "exec"), tglob)  # pylint: disable=exec-used
    return tglob['run']
