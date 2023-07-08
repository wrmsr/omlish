import typing as ta

from omlish import dispatch
from omlish.graphs import dot


class DotGen:
    def __init__(self) -> None:
        super().__init__()
        self._items: ta.List[dot.Item] = []

    @dispatch.method
    def gen(self, obj: ta.Any) -> None:
        raise TypeError(obj)

