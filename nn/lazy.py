import typing as ta
import weakref

from omlish import check
from omlish import dataclasses as dc
from omlish import lang

from .dims import Shape
from .ops import BinaryOp
from .ops import LoadOp
from .ops import Op
from .ops import UnaryOp
from .raw import RawBuffer
from .raw import RawCpuBuffer
from .shapetracker import ShapeTracker


class Lazy(lang.Abstract, lang.Sealed):
    pass


@dc.dataclass(frozen=True)
class LazyOp(Lazy):
    op: Op
    srcs: ta.Sequence[Lazy]
    arg: ta.Any = None

    @property
    def buffers(self) -> ta.Iterator['LazyBuffer']:
        for s in self.srcs:
            if isinstance(s, LazyOp):
                yield from s.buffers
            elif isinstance(s, LazyBuffer):
                yield s

    @property
    def ops(self) -> ta.Iterator['LazyOp']:
        yield self
        for s in self.srcs:
            if isinstance(s, LazyOp):
                yield from s.ops


class LazyBuffer(Lazy):
    def __init__(self, st: ShapeTracker, op: LazyOp) -> None:
        super().__init__()

        self._st = check.isinstance(st, ShapeTracker)
        self._op = check.isinstance(op, LazyOp)

        self._realized: ta.Optional[RawBuffer] = None
        self._children: ta.MutableSet['LazyBuffer'] = weakref.WeakSet()

        for b in op.buffers:
            b._children.add(self)

    @property
    def shape(self) -> Shape:
        return self._st.shape

    def binary_op(self, op: BinaryOp, y: 'LazyBuffer') -> 'LazyBuffer':
        raise NotImplementedError

    def realize(self) -> 'LazyBuffer':
        if self._realized is None:
            if self._op.op == LoadOp.FROM_CPU:
                self._realized = RawCpuBuffer.from_cpu(self._op.arg)

            elif self._op.op == BinaryOp.MUL:
                raise NotImplementedError

            else:
                raise TypeError(self._op.op)

        return self

    @property
    def is_realized(self) -> bool:
        return self._realized is not None

    def realized(self) -> RawBuffer:
        if self._realized is None:
            raise RuntimeError('Not realized')
        return self._realized


def elementwise_op(op: ta.Union[UnaryOp, BinaryOp], *srcs: LazyBuffer, arg: ta.Optional[ta.Any] = None) -> LazyBuffer:
    return LazyBuffer(
        ShapeTracker.of(srcs[0].shape),
        LazyOp(
            op,
            srcs,
            arg=arg,
        ),
    )
