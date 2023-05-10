import typing as ta
import weakref

from omlish import check
from omlish import dataclasses as dc
from omlish import lang

from .devices import Device
from .dims import Shape
from .dtypes import Dtype
from .numpy import LazyNpArray
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


def map_buffers(srcs: ta.Mapping[Lazy, Lazy], x: LazyOp) -> LazyOp:
    check.isinstance(x, LazyOp)
    if srcs and x in srcs:
        return map_buffers(srcs, srcs[x])  # type: ignore

    return LazyOp(
        x.op,
        tuple(map_buffers(srcs, y) if isinstance(y, LazyOp) else srcs[y] for y in x.srcs),
        x.arg,
    )


class LazyBuffer(Lazy):
    def __init__(
            self,
            device: Device,
            st: ShapeTracker,
            op: LazyOp,
            dtype: Dtype,
    ) -> None:
        super().__init__()

        self._device = check.isinstance(device, Device)
        self._st = check.isinstance(st, ShapeTracker)
        self._op = check.isinstance(op, LazyOp)
        self._dtype = check.isinstance(dtype, Dtype)

        self._realized: ta.Optional[RawBuffer] = None
        self._children: ta.MutableSet['LazyBuffer'] = weakref.WeakSet()

        for b in op.buffers:
            b._children.add(self)

    @property
    def device(self) -> Device:
        return self._device

    @property
    def shape(self) -> Shape:
        return self._st.shape

    @property
    def op(self) -> LazyOp:
        return self._op

    @property
    def dtype(self) -> Dtype:
        return self._dtype

    def binary_op(self, op: BinaryOp, y: 'LazyBuffer') -> 'LazyBuffer':
        raise NotImplementedError

    # # shrink -> stride -> permute -> reshape -> pad -> expand
    # def movement_op(self: 'LazyBuffer', op: MovementOp, arg: ta.Tuple[ta.Any, ...]) -> 'LazyBuffer':
    #     if op == MovementOp.RESHAPE and self.shape == arg:
    #         return self
    #
    #     # TODO: look into why that copy is needed
    #     local_st = ShapeTracker(self.shape).movement_op(op, arg)
    #
    #     # instant nops
    #     if local_st.contiguous and self.shape == local_st.shape:
    #         return self
    #
    #     # two ops in a row is one op. merge them if unresolved
    #     if self.realized is None and self.op.op == op:
    #         # TODO: why is deleting self from children needed? shouldn't GC do it?
    #         self.op.src[0].children.discard(self)
    #
    #         if op in [MovementOps.RESHAPE, MovementOps.EXPAND]:
    #             return self.op.src[0].movement_op(op, arg)
    #
    #         if op == MovementOps.SHRINK:
    #             return self.op.src[0].movement_op(
    #                 op,
    #                 tuple(
    #                     (b1 + b2, b1 + e2)
    #                     for (b1, e1), (b2, e2)
    #                     in zip(self.op.arg, arg)
    #                 ),
    #             )
    #
    #         if op == MovementOps.PERMUTE:
    #             return self.op.src[0].movement_op(op, tuple(self.op.arg[i] for i in arg))
    #
    #         if op == MovementOps.PAD:
    #             return self.op.src[0].movement_op(
    #                 op,
    #                 tuple((b1 + b2, e1 + e2) for (b1, e1), (b2, e2) in zip(self.op.arg, arg)),
    #             )
    #
    #         if op == MovementOps.STRIDE:
    #             return self.op.src[0].movement_op(op, tuple(i * j for i, j in zip(arg, self.op.arg)))
    #
    #     # some permutes are actually just reshapes
    #     if op == MovementOps.PERMUTE and local_st.contiguous:
    #         return self.movement_op(MovementOps.RESHAPE, tuple(self.shape[i] for i in arg))
    #
    #     # move permutes before expands (always, this is safe)
    #     if op == MovementOps.PERMUTE and self.realized is None and self.op.op == MovementOps.EXPAND:
    #         self.op.src[0].children.discard(self)
    #         return self.op.src[0] \
    #             .movement_op(MovementOps.PERMUTE, arg) \
    #             .movement_op(MovementOps.EXPAND, tuple(self.op.arg[a] for a in arg))
    #
    #     # create the buffer
    #     ret = create_lazybuffer(
    #         self.device,
    #         ShapeTracker(self.st).movement_op(op, arg),
    #         MovementOp,
    #         LazyOp(op, (self,), arg),
    #         self.dtype,
    #     )
    #
    #     # if the ShapeTracker becomes contiguous, replace the whole thing with a reshape (or nothing if shapes match)
    #     # NOTE: if ret is in the cache, it can already be realized
    #     if REMOVE_MOVEMENT_NOPS and ret.realized is None and self.realized is None and ret.st.contiguous:
    #         # MovementOp aren't stacked any more, they each have one parent, find the root
    #         root = get_movementroot(self)
    #         if root.st.contiguous and root != self and prod(ret.st.shape) == prod(root.shape):
    #             return root.movement_op(MovementOp.RESHAPE, ret.st.shape)
    #
    #     return ret

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

    def _eval_binary_op(self) -> LazyOp:
        # real_srcs: ta.Dict[LazyBuffer, ta.Union[LazyOp, LazyBuffer, None]] = {x: None for x in self._op.buffers}
        #
        # intermediate_shape = self.shape
        # # reshape all the late ops into the output shape
        # # NOTE: these RESHAPEs will return self if they don't change the shape
        # for x in real_srcs.keys():
        #     if real_srcs[x] is None:
        #         real_srcs[x] = x.movement_op(MovementOp.RESHAPE, intermediate_shape)
        #
        # ast = map_buffers(real_srcs, self.op)
        # return LazyOp(MovementOp.RESHAPE, (ast,), self.shape) if intermediate_shape != self.shape else ast
        raise NotImplementedError

    @staticmethod
    def from_cpu(x: LazyNpArray, device: Device) -> 'LazyBuffer':
        return LazyBuffer(
            device,
            ShapeTracker.of(x.shape),
            LazyOp(LoadOp.FROM_CPU, (), x),
            x.dtype,
        )


def elementwise_op(
        op: ta.Union[UnaryOp, BinaryOp],
        *srcs: LazyBuffer,
        arg: ta.Optional[ta.Any] = None,
) -> LazyBuffer:
    check.not_empty(srcs)

    out_device = srcs[0].device
    out_shape = srcs[0].shape
    if op == UnaryOp.CAST:
        out_dtype = check.isinstance(arg, Dtype)
    else:
        out_dtype = srcs[0].dtype  # FIXME: max(x.dtype for x in srcs)

    return LazyBuffer(
        out_device,
        ShapeTracker.of(out_shape),
        LazyOp(
            op,
            srcs,
            arg=arg,
        ),
        out_dtype,
    )
