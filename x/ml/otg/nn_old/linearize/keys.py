import io
import itertools
import typing as ta

from omlish import check
from omlish import collections as col
from omlish import dispatch
from omlish.collections import coerce

from .. import ops
from ..buffers import Buffer
from ..dims import Shape
from ..dims import Stride
from ..dtypes import Dtype
from ..raw import RawBuffer
from ..raw import RawConst
from ..shapetracker import ShapeTracker
from ..shapetracker import View


class KeyRenderer:
    def __init__(self, write: ta.Callable[[str], ta.Any], bufs: ta.Sequence[Buffer]) -> None:
        super().__init__()

        self._write = check.callable(write)
        self._bufs = coerce.seq_of(check.of_isinstance(Buffer))(bufs)
        self._buf_idx_map: ta.Mapping[Buffer, int] = col.IdentityKeyDict((buf, i) for i, buf in enumerate(self._bufs))  # noqa
        self._seen_bufs: ta.MutableSet[Buffer] = col.IdentitySet()

    @dispatch.method
    def render(self, obj: ta.Any) -> None:
        raise TypeError(obj)

    @render.register
    def render_shape(self, sh: Shape) -> None:
        self._write(f'Shape({", ".join(map(str, sh))})')

    @render.register
    def render_stride(self, st: Stride) -> None:
        self._write(f'Stride({", ".join(map(str, st))})')

    @render.register
    def render_view(self, v: View) -> None:
        self._write('View(')
        self.render(v.shape)
        self._write(', ')
        self.render(v.stride)
        self._write(f', offset={v.offset}')
        if v.mask is not None:
            raise NotImplementedError
        self._write(')')

    @render.register
    def render_shape_tracker(self, st: ShapeTracker) -> None:
        self._write('ShapeTracker(')
        for i, v in enumerate(st.views):
            if i > 0:
                self._write(', ')
            self.render(v)
        self._write(')')

    @render.register
    def render_dtype(self, dt: Dtype) -> None:
        self._write(dt.name)

    @render.register
    def render_raw_buffer(self, rb: RawBuffer) -> None:
        self._write(f'{type(rb).__name__}(size={rb.size}, ')
        self.render(rb.dtype)
        self._write(')')

    @render.register
    def render_raw_const(self, rb: RawConst) -> None:
        self._write(f'{type(rb).__name__}({rb.c}, ')
        self.render(rb.dtype)
        self._write(')')

    @render.register
    def _render_buffer(self, buf: Buffer) -> None:
        self._write(f'{type(buf).__name__}:{self._buf_idx_map[buf]}')
        if buf not in self._seen_bufs:
            self._seen_bufs.add(buf)
            self._write(f'(')
            self.render(buf.dtype)
            self._write(', ')
            if buf.is_realized:
                self.render(buf.get_realized())
            else:
                self.render(buf.get_op())
            self._write(', ')
            self.render(buf.shape_tracker)
            self._write(f')')

    @render.register
    def _render_op(self, op: ops.Op) -> None:
        self._write(f'{type(op).__name__}(')
        for i, x in enumerate(itertools.chain(op.srcs, op.args)):
            if i > 0:
                self._write(', ')
            self.render(x)


def render_key(op: ops.Op, bufs: ta.Sequence[Buffer]) -> str:
    buf = io.StringIO()
    KeyRenderer(buf.write, bufs).render(op)
    return buf.getvalue()
