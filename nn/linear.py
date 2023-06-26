import io
import typing as ta

from omlish import cached
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
    def op(self) -> LazyOp:
        return self._op

    @property
    def buffers(self) -> ta.Sequence[LazyBuffer]:
        return self._bufs

    @cached.property
    def analysis(self) -> LinearAnalysis:
        return LinearAnalyzer().analyze(ops2.convert_from_lazy_op(self._op))  # noqa

    @property
    def key(self) -> str:
        return self._key

    @cached.property
    def reduce_op(self) -> ta.Optional[LazyOp]:
        # there's only allowed to be one reduce op
        reduce_ops = [x for x in self._op.ops if isinstance(x.op, ReduceOp)]
        return check.single(reduce_ops) if reduce_ops else None  # noqa

    @cached.property
    def early_buffers(self) -> ta.Sequence[LazyBuffer]:
        # get early bufs, before the one reduce op
        return col.unique(self.reduce_op.buffers) if self.reduce_op is not None else []  # noqa

    @cached.property
    def full_buffer_index(self) -> int:
        return self.buffers.index(self.early_buffers[0]) if len(self.early_buffers) > 0 else 0

    @property
    def full_shape(self) -> Shape:
        return self._sts[self.full_buffer_index].shape

    @property
    def first_reduce(self) -> int:
        return [
            x != y
            for x, y in zip(
                self._sts[0].shape[: self.shape_len - self.upcasted] + (0,),
                self.full_shape[: self.shape_len - self.upcasted] + (1,),
                )
        ].index(True)

    @property
    def shape_len(self) -> int:
        return len(self._sts[0].shape)

    _sts: ta.List[ShapeTracker]

    _group_for_reduce: ta.List[int]
    _upcasted: int
    _local_dims: int

    def build(self) -> Program:
        # mem_est = sum(  # noqa
        #     x.dtype.item_size * (x.get_realized().size if x.is_realized is not None else x.shape.prod)
        #     for x in self._bufs
        # )

        # create new shapetrackers inside this kernel, we will permute them
        self._sts = [x.shape_tracker.copy() for x in self._bufs]
        for st in self._sts:
            st.simplify()

        # make the output buffer shape correct in here
        self._sts[0].reshape(self.analysis.shape)

        # move all reduce axes to the end
        reduce = list(enumerate(zip(self.full_shape, self._sts[0].shape)))
        permute = tuple(
            [i for i, (s, n) in reduce if s == n]
            + [i for i, (s, n) in reduce if s != n]
        )
        self.reshape_and_permute(None, permute)

        self._group_for_reduce = []
        self._upcasted = 0
        self._local_dims = 0

        # group simplifies
        self.simplify_ones()
        self.simplify_merge_adjacent()

        raise NotImplementedError

    def reshape_and_permute(
            self,
            new_shape_fn: ta.Optional[ta.Callable[[Shape], Shape]] = None,
            axis: ta.Optional[ta.Sequence[int]] = None,
    ) -> None:
        for st in self._sts:
            if new_shape_fn is not None:
                st.reshape(Shape(new_shape_fn(st.shape)))
            if axis is not None:
                st.permute(tuple(axis))

    def simplify_ones(self) -> None:
        # remove places where the shape is all ones
        # TODO: this should be factored in to multi shape stride
        if self.shape_len == 0:
            return

        all_ones = [
            all(st.shape[i] == 1 for st in self._sts)
            for i in range(self.shape_len)
        ]

        # keep at least 1 one
        if all(all_ones):
            all_ones[-1] = False

        self.reshape_and_permute(
            lambda shape: Shape(x for i, x in enumerate(shape) if not all_ones[i]),
            None,
        )

    def simplify_merge_adjacent(self):
        if self.shape_len == 0:
            return

        shapes = [x.shape for x in self._sts]
        strides = [x.views[-1].stride for x in self._sts]

        # merge dimensions if we can, multi get_shape_strides
        # TODO: does this always preserve the reduce dimension, NO
        # TODO: move this into shapetracker, with tests!
        rets = [[(shapes[j][0], strides[j][0])] for j in range(len(shapes))]
        for i in range(1, len(shapes[0])):
            can_merge = []
            for j in range(len(shapes)):
                # TODO: added the always mergeability of 1s, is this right? if so, add to shapetracker in the 1 case
                can_merge.append(
                    (strides[j][i] != 0 and rets[j][-1][1] == shapes[j][i] * strides[j][i]) or
                    (strides[j][i] == 0 and rets[j][-1][1] == 0)
                )

            # more can merge than this
            mergeable = all(can_merge) and i != self.first_reduce
            for j in range(len(shapes)):
                if mergeable:
                    rets[j][-1] = (rets[j][-1][0] * shapes[j][i], strides[j][i])
                else:
                    rets[j].append((shapes[j][i], strides[j][i]))

        # do the reshapes
        for i, x in enumerate(rets):
            self._sts[i].reshape(Shape(y[0] for y in x))


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
