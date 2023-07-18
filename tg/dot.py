import typing as ta

from omlish import check
from omlish import collections as col
from omlish import dispatch
from omlish.graphs import dot

from tinygrad.lazy import LazyBuffer
from tinygrad.ops import LazyOp
from tinygrad.ops import MovementOps
from tinygrad.runtime.lib import RawBuffer
from tinygrad.tensor import Tensor


def _gen_id(o: ta.Any) -> str:
    return hex(id(o))[2:]


class TgDotGen:

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
        self._items.append(dot.Edge(nid, self.add(x.lazydata)))
        return nid

    @_add.register
    def _add_buffer(self, buf: LazyBuffer) -> str:
        nid = _gen_id(buf)
        self._items.append(dot.Node(nid, {'label': [
            [f'{type(buf).__name__}:{nid}'],
        ]}))
        src: ta.Any
        if buf.op is not None:
            src = buf.op
        elif buf.realized is not None:
            src = buf.realized
        else:
            raise ValueError(buf)
        self._items.append(dot.Edge(nid, self.add(src)))
        return nid

    @_add.register
    def _add_op(self, op: LazyOp) -> str:
        nid = _gen_id(op)
        lbl: ta.List[ta.Any] = [[f'{op.op}:{nid}']]
        if isinstance(op.op, MovementOps):
            lbl.append([repr(check.single(op.arg))])
        self._items.append(dot.Node(nid, {'label': lbl}))
        for s in op.src:
            self._items.append(dot.Edge(nid, self.add(s)))
        return nid

    @_add.register
    def _add_raw_buffer(self, rb: RawBuffer) -> str:
        nid = _gen_id(rb)
        self._items.append(dot.Node(nid, {'label': [
            [f'{type(rb).__name__}:{nid}'],
        ]}))
        return nid


def open_tg_dot(
        obj: ta.Any,
        *,
        timeout_s: float = 10.,
        sleep_s: float = 1.,
        **kwargs: ta.Any
) -> None:
    g = TgDotGen.graph(obj, **kwargs)
    dot.open_dot(dot.render(g), timeout_s=timeout_s, sleep_s=sleep_s)
