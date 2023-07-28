import typing as ta

from omlish import check
from omlish import collections as col
from omlish import dataclasses as dc
from omlish import dispatch

from .. import ops
from ..buffers import Buffer
from ..dims import Shape
from ..dtypes import Dtype
from ..shapetracker import ShapeTracker


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
    def _analyze_buffer(self, buf: Buffer) -> LinearAnalysis:
        return LinearAnalysis(
            buf,
            buf.shape,
            buf.dtype,
            0,
        )

    @_analyze.register
    def _analyze_unary_op(self, op: ops.UnaryOp) -> LinearAnalysis:
        xa = self._analyze(op.x)
        return LinearAnalysis(
            op,
            xa.shape,
            xa.dtype,
            xa.flops + xa.shape.prod,
            )

    @_analyze.register
    def _analyze_cast(self, op: ops.Cast) -> LinearAnalysis:
        raise TypeError(op)

    @_analyze.register
    def _analyze_binary_op(self, op: ops.BinaryOp) -> LinearAnalysis:
        xa = self._analyze(op.x)
        ya = self._analyze(op.y)
        return LinearAnalysis(
            op,
            xa.shape,
            check.equal(xa.dtype, ya.dtype),
            xa.flops + ya.flops + xa.shape.prod,
            )

    @_analyze.register
    def _analyze_reduce_op(self, op: ops.ReduceOp) -> LinearAnalysis:
        xa = self._analyze(op.x)
        return LinearAnalysis(
            op,
            op.new_shape,
            xa.dtype,
            xa.flops + xa.shape.prod,
            )

    @_analyze.register
    def _analyze_where_op(self, op: ops.Where) -> LinearAnalysis:
        xa = self._analyze(op.x)
        ya = self._analyze(op.y)
        za = self._analyze(op.z)
        return LinearAnalysis(
            op,
            xa.shape,
            xa.dtype,
            xa.flops + ya.flops + za.flops + xa.shape.prod,
            )

    @_analyze.register
    def _analyze_movement_op(self, op: ops.MovementOp) -> LinearAnalysis:
        xa = self._analyze(op.x)
        return LinearAnalysis(
            op,
            ShapeTracker(xa.shape).movement_op(type(op), op.args).shape,
            xa.dtype,
            xa.flops,
        )
