import math
import typing as ta

from omlish import cached
from omlish import check
from omlish import dataclasses as dc
from omlish import dispatch
from omlish import lang
import numpy as np

from . import ops
from . import symbolic as sym
from . import uops as uo
from .buffers import Buffer
from .dtypes import Dtype
from .dtypes import Float32
from .dtypes import Float4
from .linear import LinearCodegen
from .linear import LinearCodegenOp
from .linear import LocalBuffer
from .ops import Op
from .raw import RawConst


class CstyleSymRenderer(sym.NodeRenderer):
    @sym.NodeRenderer.render.register
    def render_div(self, n: sym.Div) -> str:
        return f'({self.render(n.a)}/{n.b})'

    @sym.NodeRenderer.render.register
    def render_and(self, n: sym.And) -> str:
        return f'({"&&".join(sorted(self.render(x) for x in n.nodes))})'


def _render_sym(n: sym.Node) -> str:
    return CstyleSymRenderer().render(n)


@dc.dataclass(frozen=True)
class CstyleDialect:
    kernel_prefix: str = ''
    buffer_prefix: str = ''
    buffer_suffix: str = ''
    smem_prefix: str = ''

    barrier: str = ''

    gid: ta.Sequence[str] = ()
    lid: ta.Sequence[str] = ()

    extra_params: ta.Sequence[str] = ()

    float4: ta.Optional[str] = None

    half_prekernel: ta.Optional[str] = None
    double_prekernel: ta.Optional[str] = None

    uses_vload: bool = False


class CstyleRenderer:

    def __init__(
            self,
            uops: ta.Sequence[uo.Uop],
            bufs: ta.Sequence[ta.Union[Buffer, LocalBuffer]],
            dialect: CstyleDialect,
    ) -> None:
        super().__init__()

        self._uops = uops
        self._bufs = bufs
        self._dialect = check.isinstance(dialect, CstyleDialect)

        self._buf_names = [
            b.name if isinstance(b, LocalBuffer) else f'data{i}'
            for i, b in enumerate(self._bufs)
        ]

        self._global_size: ta.List[int] = []
        self._local_size: ta.List[int] = []
        self._lines: ta.List[str] = []
        self._depth = 0
        self._pend_close: ta.Optional[str] = None

    class Rendered(ta.NamedTuple):
        src: str
        global_size: ta.Sequence[int]
        local_size: ta.Sequence[int]

    @lang.cached_nullary
    def render(self) -> Rendered:
        self._lines.append(
            f'{self._dialect.kernel_prefix} void KERNEL_NAME_PLACEHOLDER({", ".join(self._render_params())}) {{'
        )

        for u in self._uops:
            self._append_uop(u)

        self._lines.append('}')

        return CstyleRenderer.Rendered(
            '\n'.join(self._lines),
            self._global_size,
            self._local_size,
        )

    _dtype_names: ta.Final[ta.Mapping[Dtype, str]] = {  # FIXME: lol
        Float4: 'float4',
        Float32: 'float',
    }

    @lang.cached_nullary
    def _render_params(self) -> ta.Sequence[str]:
        params: ta.List[str] = []

        for i, x in enumerate(self._bufs):
            if not isinstance(x, Buffer) or (x.is_realized and isinstance(x.get_realized(), RawConst)):
                continue

            params.append(''.join([
                'const ' if i > 0 else '',
                self._dialect.buffer_prefix,
                self._dtype_names[x.dtype],
                '*',
                self._dialect.buffer_suffix,
                ' ',
                self._buf_names[i],
            ]))

        params.extend(self._dialect.extra_params)
        return params

    def _render_token(self, tok: uo.Token, with_type: bool = False) -> str:
        if with_type:
            check.none(tok.offset)
            return f'{self._dtype_names[tok.dtype]} {tok.name}'
        if tok.offset is None:
            return tok.name
        if tok.dtype == Float4:
            return tok.name + '.' + 'xyzw'[int(tok.offset)]
        raise TypeError(tok)

    def _render_const(self, x: ta.Union[float, int], var_dtype: Dtype) -> str:
        if math.isnan(x):
            val = 'NAN'
        elif math.isinf(x):
            val = ('-' if x < 0 else '') + 'INFINITY'
        else:
            val = f'{x}' + ('' if var_dtype.is_int else 'f')
        return f'{self._dialect.float4}({val}, {val}, {val}, {val})' if var_dtype == Float4 else val

    def _render_load(self, output_dtype: Dtype, buf_name: str, buf_dtype: Dtype, idx: sym.Node, local=False) -> str:
        if output_dtype == Float4:
            return (
                f'({output_dtype.name})'
                f'(*('
                f'({self._dialect.smem_prefix if local else self._dialect.buffer_prefix}{buf_dtype.name}{output_dtype.sz}*)'  # noqa
                f'({buf_name}+{_render_sym(idx)})'
                f'))'
            )
        else:
            return f'{buf_name}[{_render_sym(idx)}]'

    def _render_store(self, buf_name: str, buf_dtype: Dtype, var_name: str, var_dtype: Dtype, idx: sym.Node, local: bool = False) -> str:
        if var_dtype.sz > 1:
            return (
                f'*(({self._dialect.smem_prefix if local else self._dialect.buffer_prefix}{buf_dtype.name}{var_dtype.sz}*)'  # noqa
                f'({buf_name}+{_render_sym(idx)})) = '
                f'({buf_dtype.name}{var_dtype.sz}){var_name};'
            )
        else:
            return f'{buf_name}[{_render_sym(idx)}] = {var_name};'

    def _append(self, s: str) -> None:
        self._lines.append('  ' * self._depth + s)

    @dispatch.method
    def _append_uop(self, uop: uo.Uop) -> None:
        raise TypeError(uop)

    @_append_uop.register
    def _append_loop(self, u: uo.Loop) -> None:
        for i, var in enumerate(u.idxs):
            if isinstance(var, sym.Num):
                if u.s == 'global' and self._dialect.gid:
                    self._global_size.append(1)
                if u.s == 'local' and self._dialect.lid:
                    self._local_size.append(1)
                # one number, not an index
                self._append('{')

            elif u.s == 'global' and self._dialect.gid:
                check.state(len(u.idxs) <= len(self._dialect.gid))
                self._append(f'{{ int {var.expr} = {self._dialect.gid[len(u.idxs) - 1 - i]};  /* {var.max + 1} */')
                self._global_size.append(var.max + 1)

            elif u.s == 'local' and self._dialect.lid:
                check.state(len(u.idxs) <= len(self._dialect.lid))
                self._append(f'{{ int {var.expr} = {self._dialect.lid[len(u.idxs) - 1 - i]};  /* {var.max + 1} */')
                self._local_size.append(var.max + 1)

            else:
                self._append(f'for (int {var.expr} = {var.min}; {var.expr} <= {var.max}; ++{var.expr}) {{')

        self._depth += 1

    @_append_uop.register
    def _append_end_loop(self, u: uo.EndLoop) -> None:
        if u.s == 'local' and len(self._dialect.lid):
            # TODO: this is a bit of a hack. the local loop isn't real on the GPU
            self._append(f'if ({_render_sym(sym.sum_(u.idxs))} == 0) {{')
            self._pend_close = '}' * (len(u.idxs) + 1) + f' /* {u.s} */'
        else:
            if u.s == 'global' and self._pend_close:
                self._depth -= 1
                self._append(self._pend_close)
                self._pend_close = None
            self._depth -= 1
            self._append('}' * len(u.idxs) + f' /* {u.s} */')

    @_append_uop.register
    def _append_barrier(self, u: uo.Barrier) -> None:
        self._append(self._dialect.barrier)

    @_append_uop.register
    def _append_const(self, u: uo.Const) -> None:
        check.not_none(u.out)
        self._append(f'{self._render_token(u.out, True)} = {self._render_const(u.v, u.out.dtype)};')

    _code_for_op: ta.Final[ta.Mapping[ta.Type[ops.Op], ta.Callable[..., str]]] = {
        ops.Exp2: lambda x: f'exp2({x})',
        ops.Log2: lambda x: f'log2({x})',
        ops.Sqrt: lambda x: f'sqrt({x})',
        ops.Sin: lambda x: f'sin({x})',

        ops.Add: lambda a, b: f'({a}+{b})',
        ops.Sub: lambda a, b: f'({a}-{b})',
        ops.Mul: lambda a, b: f'({a}*{b})',
        ops.Div: lambda a, b: f'({a}/{b})',
        ops.Maximum: lambda a, b: f'max({a},{b})',
        ops.CmpEq: lambda a, b: f'({a}=={b})',
        ops.MulAcc: lambda a, b, c: f'(({a}*{b})+{c})',
    }

    @_append_uop.register
    def _append_alu(self, u: uo.Alu) -> None:
        check.not_none(u.out)
        self._append(
            f'{self._render_token(u.out, u.out not in u.vin)} = '
            f'{self._code_for_op[u.ty](*[self._render_token(x) for x in u.vin])};'
        )

    class _Cast(ta.NamedTuple):
        prefix: str
        zero: str

    @cached.property
    def _casts_by_dtype(self) -> ta.Mapping[Dtype, _Cast]:
        return {
            Float32: self._Cast('(float)', '0.0f'),
            Float4: self._Cast('', f'{self._dialect.float4}(0.0f, 0.0f, 0.0f, 0.0f)'),
        }

    @_append_uop.register
    def _append_load(self, u: uo.Load) -> None:
        out = check.not_none(u.out)
        buf = self._bufs[u.i]

        if u.valid.max == 0:
            val = self._render_const(0.0, out.dtype)
        elif buf.is_realized and isinstance(buf.get_realized(), RawConst):
            val = self._render_const(self._bufs[u.i].get_realized()._buf, out.dtype)  # FIXME:
        else:
            val = self._render_load(
                out.dtype,
                self._buf_names[u.i],
                buf.dtype,
                u.idx,
                isinstance(buf, LocalBuffer),
            )
        if u.valid.min == 0 and u.valid.max == 1:
            val = f"({_render_sym(u.valid)}) ? ({val}) : {self._render_const(0.0, out.dtype)}"
        self._append(f'{self._render_token(out, True)} = {val};')

    @_append_uop.register
    def _append_store(self, u: uo.Store) -> None:
        self._append(
            self._render_store(
                self._buf_names[u.i],
                self._bufs[u.i].dtype,
                self._render_token(u.vin[0]),
                u.vin[0].dtype if u.vin[0].offset is None else Float32,
                u.idx,
                isinstance(self._bufs[u.i], LocalBuffer),
            )
        )

    @_append_uop.register
    def _append_cast(self, u: uo.Cast) -> None:
        check.state(u.out.dtype == Float4)
        self._append(
            f'{self._render_token(u.out)} = '
            f'{self._dialect.float4}({",".join([self._render_token(x) for x in u.vin])});'
        )

    @_append_uop.register
    def _append_define_local(self, u: uo.DefineLocal) -> None:
        self._append(self._dialect.smem_prefix + f'float {u.s}[{u.sz}];')


class CStyleCodegenOp(LinearCodegenOp):
    pass


class CstyleCodegen(LinearCodegen):
    def op(self, op: Op, output: Buffer) -> LinearCodegenOp:
        return CStyleCodegenOp(op, output)
