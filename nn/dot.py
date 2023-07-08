import typing as ta

from omlish import collections as col
from omlish import dispatch
from omlish.graphs import dot

from .buffers import Buffer
from .ops import Op
from .raw import RawBuffer
from .tensor import Tensor


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
    def _add_tensor(self, obj: Tensor) -> str:
        nid = str(id(obj))
        self._items.append(dot.Node(nid, {'label': f'{type(obj).__name__}:{id(obj)}'}))
        self._items.append(dot.Edge(nid, self.add(obj.data)))
        return nid

    @_add.register
    def _add_buffer(self, obj: Buffer) -> str:
        nid = str(id(obj))
        self._items.append(dot.Node(nid, {'label': f'{type(obj).__name__}:{id(obj)}'}))
        self._items.append(dot.Edge(nid, self.add(obj.src)))
        return nid

    @_add.register
    def _add_op(self, obj: Op) -> str:
        nid = str(id(obj))
        self._items.append(dot.Node(nid, {'label': f'{type(obj).__name__}:{id(obj)}'}))
        for s in obj.srcs:
            self._items.append(dot.Edge(nid, self.add(s)))
        return nid

    @_add.register
    def _add_raw_buffer(self, obj: RawBuffer) -> str:
        nid = str(id(obj))
        self._items.append(dot.Node(nid, {'label': f'{type(obj).__name__}:{id(obj)}'}))
        return nid
