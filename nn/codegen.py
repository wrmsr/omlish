import abc
import typing as ta

from omlish import check
from omlish import collections as col
from omlish import dataclasses as dc
from omlish import dispatch
from omlish import lang

from .dims import Shape
from .dtypes import Dtype
from .lazy import LazyBuffer
from .lazy import LazyOp
from .ops import MovementOp


class Program(lang.Abstract):
    @property
    @abc.abstractmethod
    def name(self) -> str:
        raise NotImplementedError

    @abc.abstractmethod
    def exec(self, bufs: ta.Sequence[LazyBuffer]) -> None:
        raise NotImplementedError


class CodegenOp(lang.Abstract):
    @property
    @abc.abstractmethod
    def key(self) -> str:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def buffers(self) -> ta.Sequence[LazyBuffer]:
        raise NotImplementedError

    @abc.abstractmethod
    def build(self) -> Program:
        raise NotImplementedError


class Codegen(lang.Abstract):
    @abc.abstractmethod
    def op(self, op: LazyOp, output: LazyBuffer) -> CodegenOp:
        raise NotImplementedError


##


from . import ops2  # noqa


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


class LinearCodegenOp(CodegenOp):
    def __init__(self, op: LazyOp, output: LazyBuffer) -> None:
        super().__init__()

        # NOTE: if there's a RESHAPE, we skip it. the output shape is set from the reduce op or a latebuf
        self._op = check.isinstance(op.srcs[0], LazyOp) if op.op == MovementOp.RESHAPE else op

        # get the output buffers
        self._bufs = [output, *col.unique(op.buffers)]

        # FIXME: ... lol... formalized keyifier plz - str is right though
        # bufs are needed because kernels like f(x) = x + x and f(x, y) = x + y have the same str(ast), but are
        # different kernels. mapping the buffers to integers is required because a-b != b-a (and how would you tell a
        # and b apart?)
        # self._key = (
        #     f'LinearCodegenOp '
        #     f'op={str(map_buffers({x: i for i, x in enumerate(self._bufs)}, op))} '  # FIXME: oof...
        #     f'bufs={self._bufs}'
        # )
        self._key = '???'

    @property
    def key(self) -> str:
        return self._key

    @property
    def buffers(self) -> ta.Sequence[LazyBuffer]:
        return self._bufs

    def build(self) -> Program:
        a = LinearAnalyzer().analyze(ops2.convert_from_lazy_op(self._op))  # noqa
        raise NotImplementedError


class LinearCodegen(Codegen):
    def op(self, op: LazyOp, output: LazyBuffer) -> CodegenOp:
        return LinearCodegenOp(op, output)


##


class CStyleCodegenOp(LinearCodegenOp):
    pass


class CstyleCodegen(LinearCodegen):
    def op(self, op: LazyOp, output: LazyBuffer) -> CodegenOp:
        return CStyleCodegenOp(op, output)
