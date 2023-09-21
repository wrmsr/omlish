import itertools
import typing as ta

from omlish import collections as col
from omlish import dataclasses as dc

from .. import dtypes as dt
from .. import ops
from ..buffers import Buffer
from ..raw import RawConst

from tinygrad.ops import LazyOp, MovementOps, FlopCounter, get_lazyop_info, ReduceOps
from tinygrad.lazy import LazyBuffer
from tinygrad.helpers import dedup, dtypes, colored, ImageDType, DType
from tinygrad.shape.shapetracker import ShapeTracker
from tinygrad.shape.symbolic import sint
from tinygrad.shape.view import strides_for_shape


@dc.dataclass(frozen=True)
class LocalBuffer:
    name: str
    size: int
    dtype: dt.Dtype = dt.Float32
    realized: ta.Any = None

    def __str__(self) -> str:
        return f'localbuffer<{self.name}[{self.size}]>'


@dc.dataclass(frozen=True)
class KernelOptions:
    # TODO: make this generic with a list of supported types
    supports_float4: bool = True
    supports_float4_alu: bool = True
    
    has_local: bool = True
    
    # NOTE: these two should be in z,y,x(reversed) order for cstyle backends, they are flipped when kernel is rendered
    global_max: ta.Optional[ta.Sequence[int]] = None
    local_max: ta.Optional[ta.Sequence[int]] = None


def buf_is_kernel_arg(x: Buffer) -> bool:
    return x.is_realized and not isinstance(x.get_realized(), RawConst)


class Kernel:
    def __init__(
        self,
        op: ops.Op,
        output_buffer: Buffer,
        opts: ta.Optional[KernelOptions] = None,
    ) -> None:
        super().__init__()

        # NOTE: if there's a RESHAPE, we skip it. the output shape is set from the reduce op or a latebuf
        self.op = op.srcs[0] if isinstance(op, ops.Reshape) else op
        self.opts = opts if opts else KernelOptions()

        # get the output buffers
        self.bufs = [output_buffer] + col.unique(op.buffers)
        self.arg_bufs = {
            x: f'data{i}'
            for i, x in enumerate(
                dedup([x.get_realized() for x in self.bufs if buf_is_kernel_arg(x)])
            )
        }

        # key for lookup in cache (can change, str might not be right)
        # bufs are needed because kernels like f(x) = x + x and f(x, y) = x + y have the same str(ast), but are
        # different kernels. mapping the buffers to integers is required because a-b != b-a (and how would you tell a
        # and b apart?)
        self.key = (
            ast.map_buffers(
                {
                    x: (self.arg_bufs[x.get_realized()] if x.is_realized in self.arg_bufs else x)
                    for x in self.bufs
                }
            ).key,
            tuple([x.key for x in self.bufs]),
        )

    def process(self) -> None:
        if hasattr(self, "sts"):
            return  # already processed

        # fetch lazyop info
        self.info: FlopCounter = get_lazyop_info(cast(LazyOp, self.ast))
        self.mem_estimate: int = sum(
            x.dtype.itemsize * x.size for x in self.arg_bufs.keys()
        )

        # there's only allowed to be one reduceop
        reduceops = [x for x in self.ast.get_lazyops() if x.op in ReduceOps]
        assert len(dedup(reduceops)) <= 1, "max one reduce op in an ast"
        self.reduceop = reduceops[0] if reduceops else None

        # get earlybufs, before the one reduce op
        self.earlybufs = dedup(self.reduceop.buffers) if self.reduceop else []

        # create new shapetrackers inside this kernel, we will permute them
        self.sts: ta.List[ShapeTracker] = [x.st.copy() for x in self.bufs]
        for st in self.sts:
            st.simplify()

        # make the output buffer shape correct in here
        self.sts[0].reshape(self.info.shape)
        self.full_buf_index: int = (
            self.bufs.index(self.earlybufs[0]) if self.earlybufs else 0
        )

        # parameters
        self.group_for_reduce: ta.List[int] = []
        self.upcasted: int = 0
        self.local_dims: int = 0
        self.local_alias: ta.Dict[int, LocalBuffer] = {}
        self.use_tensor_cores: bool = False
        self.exclude_local_upcast: int = 0
        self.reverse_upcast_dir: bool = False

        self.global_size: ta.Optional[ta.List[int]] = None
        self.local_size: ta.Optional[ta.List[int]] = None

    def has_variable_shape(self) -> bool:
        for b in self.bufs:
            if any(not isinstance(x, int) for x in b.st.shape):
                return True
        return False

    def shape_offsets(self, i):
        return (
            itertools.product(
                *[
                    list(range(s))
                    for s in self.sts[i].shape[self.shape_len - self.upcasted :][::-1]
                ]
            )
            if self.upcasted > 0
            else [tuple()]
        )

    def float4_axis(self, i):
        return [
            x - (self.shape_len - self.upcasted)
            for x in self.sts[i].unit_stride_axes()
            if x >= self.shape_len - self.upcasted and self.sts[i].shape[x] % 4 == 0
        ]

    def upcasted_axis(self, i):
        return list(
            zip(
                self.sts[i].shape[self.shape_len - self.upcasted :],
                self.sts[i].real_strides()[self.shape_len - self.upcasted :],
                [
                    x != y
                    for x, y in zip(
                        self.sts[0].shape[self.shape_len - self.upcasted :],
                        self.full_shape[self.shape_len - self.upcasted :],
                    )
                ],
            )
        )

    # TODO: is there a better way to write this?
    def acc_offsets(self, i):
        if self.upcasted == 0:
            return [0]
        upcasted_i = self.upcasted_axis(i)
        acc_strides = [
            x * (1 - upcasted_i[::-1][i][2])
            for i, x in enumerate(
                strides_for_shape(tuple(1 if r else s for s, _, r in upcasted_i[::-1]))
            )
        ]
        return [
            sum(t)
            for t in itertools.product(
                *[
                    [y * acc_strides[i] for y in range(x[0])]
                    for i, x in enumerate(upcasted_i[::-1])
                ]
            )
        ]

    def get_upcast_dim(self, i) -> ta.List[int]:
        should_upcast = self.opts.supports_float4 and (
            self.bufs[i].dtype in [dtypes.float32, dtypes.float16]
            or isinstance(self.bufs[i].dtype, ImageDType)
        )
        return [
            x
            for x in self.sts[i].unit_stride_axes()
            if should_upcast
            and x >= self.shape_len - self.upcasted
            and self.sts[i].shape[x] > 1
        ]

    @property
    def first_reduce(self) -> int:
        return [
            x != y
            for x, y in zip(
                self.sts[0].shape[: self.shape_len - self.upcasted] + (0,),
                self.full_shape[: self.shape_len - self.upcasted] + (1,),
            )
        ].index(True)

    @property
    def output_shape(self) -> Tuple[sint, ...]:
        return self.sts[0].shape

    @property
    def full_shape(self) -> Tuple[sint, ...]:
        return self.sts[self.full_buf_index].shape

    @property
    def full_unupcasted_shape(self) -> Tuple[sint, ...]:
        return self.full_shape[: self.shape_len - self.upcasted]

    @property
    def shape_len(self) -> int:
        return len(self.sts[0].shape)

    @property
    def upcast_in_mid_reduce_axes(self) -> ta.List[int]:
        return [
            j
            for j in range(
                self.first_reduce, self.first_reduce + len(self.group_for_reduce)
            )
            if self.full_shape[j] == self.sts[0].shape[j]
        ]

    @property
    def global_dims(self) -> int:
        return self.first_reduce - self.local_dims

    # there's seven chunks of the shape
    # blue   -- global dims
    # cyan   -- local dims
    #  *** self.first_reduce
    # green  -- reduce-local dims
    # white  -- reduce-late upcasted dim (self.upcast_in_mid_reduce_axes)
    # red    -- reduce loops
    #  *** self.upcasted
    # purple -- reduce upcasted
    # yellow -- normal upcasted dimensions
    def colors(self) -> ta.List[str]:
        # up to first_reduce, they are all global (blue)
        colors = ["blue"] * self.global_dims
        # except the local_dims, these are non-reduce locals (cyan)
        colors += ["cyan"] * self.local_dims
        # between first_reduce and first_reduce + group_for_reduce, they are either local (cyan), or late upcasted (green)
        colors += [
            "white" if i in self.upcast_in_mid_reduce_axes else "green"
            for i in range(
                self.first_reduce, self.first_reduce + len(self.group_for_reduce)
            )
        ]
        # between first_reduce + group_for_reduce and upcasted, they are reduce (red)
        colors += ["red"] * (
            (self.shape_len - self.upcasted)
            - (self.first_reduce + len(self.group_for_reduce))
        )
        # upcasted dimensions are reduce (magenta) or normal (yellow)
        colors += [
            "magenta" if self.full_shape[i] != self.sts[0].shape[i] else "yellow"
            for i in range(self.shape_len - self.upcasted, self.shape_len)
        ]
        assert len(colors) == self.shape_len, "colors size mismatch"
        return colors

    def colored_shape(self) -> str:
        return " ".join(
            colored(s, color)
            for s, color in zip(
                [f"{s:4d}" if isinstance(s, int) else s for s in self.full_shape],
                self.colors(),
            )
        )

    def printbufs(self, prefix=""):
        for i, st in enumerate(self.sts):
            print(
                prefix,
                f"{i:3d} {str(self.bufs[i].realized) if self.bufs[i].realized is not None else str(self.bufs[i]):47s}",
                st.views,
            )
        print(self.colored_shape())
