import io
import typing as ta

from omlish import check
from omlish import collections as col
from omlish import dataclasses as dc
from omlish import dispatch
from omlish import lang
from omlish.collections import coerce

from . import ops2  # noqa
from . import symbolic as sym
from .codegen import Codegen
from .codegen import CodegenOp
from .codegen import Program
from .dims import Shape
from .dtypes import Dtype
from .lazy import LazyBuffer
from .lazy import LazyOp
from .ops import MovementOp
from .ops import ReduceOp
from .shapetracker import ShapeTracker


@dc.dataclass(frozen=True)
class LinearAnalysis:
    obj: ta.Any

    shape: Shape = dc.field(coerce=check.of_isinstance(Shape))
    dtype: Dtype = dc.field(coerce=check.of_isinstance(Dtype))
    flops: int = dc.field(coerce=check.of_isinstance(int))


class LinearAnalyzer:
    def __init__(self) -> None:
        super().__init__()

        self._dct: ta.MutableMapping[ta.Any, LinearAnalysis] = col.IdentityKeyDict()

    def analyze(self, x: ta.Any) -> LinearAnalysis:
        try:
            return self._dct[x]
        except KeyError:
            ret = self._dct[x] = self._analyze(x)
            return ret

    @dispatch.method
    def _analyze(self, x: ta.Any) -> LinearAnalysis:
        raise TypeError(x)

    @_analyze.register
    def _analyze_buffer(self, buf: ops2.Buffer) -> LinearAnalysis:
        lb = check.isinstance(buf.obj, LazyBuffer)
        return LinearAnalysis(
            buf,
            lb.shape,
            lb.dtype,
            0,
        )

    @_analyze.register
    def _analyze_unary_op(self, op: ops2.UnaryOp) -> LinearAnalysis:
        raise NotImplementedError

    @_analyze.register
    def _analyze_cast(self, op: ops2.Cast) -> LinearAnalysis:
        raise TypeError(op)

    @_analyze.register
    def _analyze_binary_op(self, op: ops2.BinaryOp) -> LinearAnalysis:
        xa = self._analyze(op.x)
        ya = self._analyze(op.y)
        return LinearAnalysis(
            op,
            xa.shape,
            check.equal(xa.dtype, ya.dtype),
            xa.flops + ya.flops + xa.shape.prod,
            )


class KeyRenderer:
    def __init__(self, writer: ta.Callable[[str], ta.Any], bufs: ta.Sequence[LazyBuffer]) -> None:
        super().__init__()

        self._writer = check.callable(writer)
        self._bufs = coerce.seq_of(check.of_isinstance(LazyBuffer))(bufs)
        self._buf_idx_map: ta.Mapping[LazyBuffer, int] = col.IdentityKeyDict((buf, i) for i, buf in enumerate(self._bufs))  # noqa

    @dispatch.method
    def render(self, obj: ta.Any) -> None:
        raise TypeError(obj)

    @render.register
    def _render_buffer(self, buf: ops2.Buffer) -> None:
        self._writer(f'{type(buf).__name__}:{self._buf_idx_map[buf.obj]}')

    @render.register
    def _render_unary_op(self, op: ops2.UnaryOp) -> None:
        self._writer(f'({type(op).__name__} ')
        self.render(op.x)
        self._writer(')')

    @render.register
    def _render_binary_op(self, op: ops2.BinaryOp) -> None:
        self._writer(f'({type(op).__name__} ')
        self.render(op.x)
        self._writer(' ')
        self.render(op.y)
        self._writer(')')


def render_key(op: LazyOp, bufs: ta.Sequence[LazyBuffer]) -> str:
    buf = io.StringIO()
    KeyRenderer(buf.write, bufs).render(ops2.convert_from_lazy_op(op))
    return buf.getvalue()


class LinearCodegenOp(CodegenOp):
    def __init__(self, op: LazyOp, output: LazyBuffer) -> None:
        super().__init__()

        # NOTE: if there's a RESHAPE, we skip it. the output shape is set from the reduce op or a latebuf
        self._op = check.isinstance(op.srcs[0], LazyOp) if op.op == MovementOp.RESHAPE else op

        self._bufs = [output, *col.unique(op.buffers)]

        self._key = render_key(op, self._bufs)

    @property
    def key(self) -> str:
        return self._key

    @property
    def buffers(self) -> ta.Sequence[LazyBuffer]:
        return self._bufs

    def build(self) -> Program:
        ana = LinearAnalyzer().analyze(ops2.convert_from_lazy_op(self._op))  # noqa
        mem_est = sum(  # noqa
            x.dtype.item_size * (x.get_realized().size if x.is_realized is not None else x.shape.prod)
            for x in self._bufs
        )

        # there's only allowed to be one reduce op
        reduce_ops = [x for x in self._op.ops if isinstance(x.op, ReduceOp)]
        reduce_op = check.single(reduce_ops) if reduce_ops else None  # noqa

        # get early bufs, before the one reduce op
        early_bufs = col.unique(reduce_op.buffers) if reduce_op is not None else []  # noqa

        # create new shapetrackers inside this kernel, we will permute them
        sts: ta.List[ShapeTracker] = [x.shape_tracker.copy() for x in self._bufs]
        for st in sts:
            st.simplify()

        raise NotImplementedError


class LinearCodegen(Codegen):
    def op(self, op: LazyOp, output: LazyBuffer) -> CodegenOp:
        return LinearCodegenOp(op, output)


##


@dc.dataclass(frozen=True)
class Token:
    name: str
    dtype: Dtype
    offset: ta.Optional[int] = None


##


@dc.dataclass(frozen=True)
class UOp(lang.Sealed, lang.Abstract):
    out: ta.Optional[Token]
    vin: ta.List[Token]


@dc.dataclass(frozen=True)
class Const(UOp):
    v: float


@dc.dataclass(frozen=True)
class Cast(UOp):
    pass


@dc.dataclass(frozen=True)
class Alu(UOp):
    ty: type  # ta.Union[ta.Type[ops2.UnaryOp], ta.Type[ops2.BinaryOp]]


@dc.dataclass(frozen=True)
class DefineLocal(UOp):
    s: str
    sz: int


#


@dc.dataclass(frozen=True)
class LoopOp(UOp, lang.Abstract):
    idxs: ta.Sequence[sym.Var]
    s: str


@dc.dataclass(frozen=True)
class Loop(LoopOp):
    pass


@dc.dataclass(frozen=True)
class EndLoop(LoopOp):
    pass


#


@dc.dataclass(frozen=True)
class MemOp(UOp, lang.Abstract):
    i: int
    idx: sym.Var
    valid: sym.Var


@dc.dataclass(frozen=True)
class Load(MemOp):
    pass


@dc.dataclass(frozen=True)
class Store(MemOp):
    pass
