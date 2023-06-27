import math
import typing as ta

from omlish import check
from omlish import dataclasses as dc
from omlish import dispatch
from omlish import lang
import numpy as np

from . import ops2
from . import symbolic as sym
from . import uops as uo
from .dtypes import Dtype
from .dtypes import Float32
from .lazy import LazyBuffer
from .lazy import LazyOp
from .linear import LinearCodegen
from .linear import LinearCodegenOp
from .linear import LocalBuffer
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
            bufs: ta.Sequence[ta.Union[LazyBuffer, LocalBuffer]],
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
            self._render_uop(u)

        self._lines.append('}')

        return CstyleRenderer.Rendered(
            '\n'.join(self._lines),
            self._global_size,
            self._local_size,
        )

    _dtype_names: ta.Final[ta.Mapping[Dtype, str]] = {  # FIXME: lol
        Float32: 'float',
    }

    @lang.cached_nullary
    def _render_params(self) -> ta.Sequence[str]:
        params: ta.List[str] = []

        for i, x in enumerate(self._bufs):
            if not isinstance(x, LazyBuffer) or (x.is_realized and isinstance(x.get_realized(), RawConst)):
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
        raise NotImplementedError

    def _line(self, s: str) -> None:
        self._lines.append('  ' * self._depth + s)

    @dispatch.method
    def _render_uop(self, uop: uo.Uop) -> None:
        raise TypeError(uop)

    @_render_uop.register
    def _render_loop(self, u: uo.Loop) -> None:
        for i, var in enumerate(u.idxs):
            if isinstance(var, sym.Num):
                if u.s == 'global' and self._dialect.gid:
                    self._global_size.append(1)
                if u.s == 'local' and self._dialect.lid:
                    self._local_size.append(1)
                # one number, not an index
                self._line('{')

            elif u.s == 'global' and self._dialect.gid:
                check.state(len(u.idxs) <= len(self._dialect.gid))
                self._line(f'{{ int {var.expr} = {self._dialect.gid[len(u.idxs) - 1 - i]};  /* {var.max + 1} */')
                self._global_size.append(var.max + 1)

            elif u.s == 'local' and self._dialect.lid:
                check.state(len(u.idxs) <= len(self._dialect.lid))
                self._line(f'{{ int {var.expr} = {self._dialect.lid[len(u.idxs) - 1 - i]};  /* {var.max + 1} */')
                self._local_size.append(var.max + 1)

            else:
                self._line(f'for (int {var.expr} = {var.min}; {var.expr} <= {var.max}; ++{var.expr}) {{')

        self._depth += 1

    @_render_uop.register
    def _render_end_loop(self, u: uo.EndLoop) -> None:
        if u.s == 'local' and len(self._dialect.lid):
            # TODO: this is a bit of a hack. the local loop isn't real on the GPU
            self._line(f'if ({_render_sym(sym.sum_(u.idxs))} == 0) {{')
            self._pend_close = '}' * (len(u.idxs) + 1) + f' /* {u.s} */'
        else:
            if u.s == 'global' and self._pend_close:
                self._depth -= 1
                self._line(self._pend_close)
                self._pend_close = None
            self._depth -= 1
            self._line('}' * len(u.idxs) + f' /* {u.s} */')

    @_render_uop.register
    def _render_barrier(self, u: uo.Barrier) -> None:
        self._line(self._dialect.barrier)

    @_render_uop.register
    def _render_const(self, u: uo.Const) -> None:
        check.not_none(u.out)
        if u.v == -math.inf:
            self._line(f'{self._render_token(u.out, True)} = -INFINITY;')
        else:
            self._line(f'{self._render_token(u.out, True)} = {u.v}f;')

    _code_for_op: ta.Final[ta.Mapping[ta.Type[ops2.Op], ta.Callable[..., str]]] = {
        ops2.Exp2: lambda x: f'exp2({x})',
        ops2.Log2: lambda x: f'log2({x})',
        ops2.Sin: lambda x: f'sin({x})',
        ops2.Add: lambda a, b: f'({a}+{b})',
        ops2.Sub: lambda a, b: f'({a}-{b})',
        ops2.Mul: lambda a, b: f'({a}*{b})',
        ops2.Div: lambda a, b: f'({a}/{b})',
        ops2.Pow: lambda a, b: f'pow({a},{b})',
        ops2.Max: lambda a, b: f'max({a},{b})',
        ops2.CmpEq: lambda a, b: f'({a}=={b})',
        ops2.MulAcc: lambda a, b, c: f'(({a}*{b})+{c})',
    }

    @_render_uop.register
    def _render_alu(self, u: uo.Alu) -> None:
        check.not_none(u.out)
        if u.out in u.vin:
            self._line(
                f'{self._render_token(u.out)} = '
                f'{self._code_for_op[u.ty](*[self._render_token(x) for x in u.vin])};'
            )
        else:
            self._line(
                f'{self._render_token(u.out, True)} = '
                f'{self._code_for_op[u.ty](*[self._render_token(x) for x in u.vin])};'
            )

    class _Cast(ta.NamedTuple):
        prefix: str
        zero: str

    _casts_by_dtype: ta.Final[ta.Mapping[Dtype, _Cast]] = {
        Float32: _Cast('(float)', '0.0f'),
    }

    @_render_uop.register
    def _render_load(self, u: uo.Load) -> None:
        out = check.not_none(u.out)
        buf = self._bufs[u.i]

        # TODO: merge with CONST?
        if buf.is_realized and isinstance(realized := buf.get_realized(), RawConst):
            check.state(out.dtype == Float32)
            x = float(check.isinstance(realized.to_cpu(), np.float))
            if math.isnan(x):
                val = 'NAN'
            elif math.isinf(x):
                val = ('-' if x < 0 else '') + 'INFINITY'
            else:
                val = f'{x}' + ('f' if not buf.dtype.is_int else '')
        else:
            val = f'{self._buf_names[u.i]}[{_render_sym(u.idx)}]'

        # NOTE: if min and max are both 0, it should be a CONST in the Linearizer
        if u.valid.min == 1:
            self._line(f'{self._render_token(out, True)} = {val};')
        else:
            cast = self._casts_by_dtype[out.dtype]
            self._line(f'{self._render_token(out, True)} = ({_render_sym(u.valid)}) ? {cast.prefix}({val}) : {cast.zero};')

    @_render_uop.register
    def _render_store(self, u: uo.Store) -> None:
        check.state(u.vin[0].dtype == Float32)
        check.state(u.valid.min == 1)
        self._line(f'{self._buf_names[u.i]}[{_render_sym(u.idx)}] = {self._render_token(u.vin[0])};')

    @_render_uop.register
    def _render_cast(self, u: uo.Cast) -> None:
        raise NotImplementedError  # FIXME: float4 only?


class CStyleCodegenOp(LinearCodegenOp):
    pass


class CstyleCodegen(LinearCodegen):
    def op(self, op: LazyOp, output: LazyBuffer) -> LinearCodegenOp:
        return CStyleCodegenOp(op, output)
