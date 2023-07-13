import typing as ta

from omlish import check
from omlish import collections as col
from omlish import dispatch
from omlish.graphs import dot

from . import ops
from .buffers import Buffer
from .raw import RawBuffer
from .tensor import Tensor


def _gen_id(o: ta.Any) -> str:
    return hex(id(o))[2:]


class DotGen:

    def __init__(self) -> None:
        super().__init__()

        self._items: ta.List[dot.Item] = []
        self._ids_by_obj: ta.MutableMapping[ta.Any, str] = col.IdentityKeyDict()

    @property
    def items(self) -> ta.Sequence[dot.Item]:
        return self._items

    @classmethod
    def graph(cls, root: ta.Any, **kwargs: ta.Any) -> dot.Graph:
        gen = cls(**kwargs)
        gen.add(root)
        return dot.Graph(gen.items)

    def add(self, obj: ta.Any) -> str:
        try:
            return self._ids_by_obj[obj]
        except KeyError:
            nid = self._ids_by_obj[obj] = self._add(obj)
            return nid

    @dispatch.method
    def _add(self, obj: ta.Any) -> str:
        raise TypeError(obj)

    @_add.register
    def _add_tensor(self, x: Tensor) -> str:
        nid = _gen_id(x)
        self._items.append(dot.Node(nid, {'label': [
            [f'{type(x).__name__}:{nid}'],
        ]}))
        self._items.append(dot.Edge(nid, self.add(x.data)))
        return nid

    @_add.register
    def _add_buffer(self, buf: Buffer) -> str:
        nid = _gen_id(buf)
        self._items.append(dot.Node(nid, {'label': [
            [f'{type(buf).__name__}:{nid}'],
        ]}))
        self._items.append(dot.Edge(nid, self.add(buf.src)))
        return nid

    @_add.register
    def _add_op(self, op: ops.Op) -> str:
        nid = _gen_id(op)
        self._items.append(dot.Node(nid, {'label': [
            [f'{type(op).__name__}:{nid}'],
        ]}))
        for s in op.srcs:
            self._items.append(dot.Edge(nid, self.add(s)))
        return nid

    @_add.register
    def _add_movement_op(self, op: ops.MovementOp) -> str:
        nid = _gen_id(op)
        self._items.append(dot.Node(nid, {'label': [
            [f'{type(op).__name__}:{nid}'],
            [repr(check.single(op.args))],
        ]}))
        for s in op.srcs:
            self._items.append(dot.Edge(nid, self.add(s)))
        return nid

    @_add.register
    def _add_raw_buffer(self, rb: RawBuffer) -> str:
        nid = _gen_id(rb)
        self._items.append(dot.Node(nid, {'label': [
            [f'{type(rb).__name__}:{nid}'],
        ]}))
        return nid


def open_dot(
        obj: ta.Any,
        *,
        timeout_s: float = 10.,
        sleep_s: float = 1.,
        **kwargs: ta.Any
) -> None:
    g = DotGen.graph(obj, **kwargs)
    dot.open_dot(dot.render(g), timeout_s=timeout_s, sleep_s=sleep_s)
