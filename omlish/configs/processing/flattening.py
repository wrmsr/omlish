# ruff: noqa: UP006 UP007 UP045
# @omlish-lite
import abc
import typing as ta

from ...lite.abstract import Abstract
from ...lite.check import check


K = ta.TypeVar('K')
V = ta.TypeVar('V')


##


class ConfigFlattening:
    DEFAULT_DELIMITER = '.'
    DEFAULT_INDEX_OPEN = '('
    DEFAULT_INDEX_CLOSE = ')'

    class _MISSING:
        def __new__(cls, *args, **kwargs):  # noqa
            raise TypeError

    def __init__(
            self,
            *,
            delimiter: str = DEFAULT_DELIMITER,
            index_open: str = DEFAULT_INDEX_OPEN,
            index_close: str = DEFAULT_INDEX_CLOSE,
    ) -> None:
        super().__init__()

        self._delimiter = check.not_empty(delimiter)
        self._index_open = check.not_empty(index_open)
        self._index_close = check.not_empty(index_close)

    def flatten(self, unflattened: ta.Mapping[str, ta.Any]) -> ta.Mapping[str, ta.Any]:
        def rec(prefix: ta.List[str], value: ta.Any) -> None:
            if isinstance(value, dict):
                for k, v in value.items():
                    rec([*prefix, k], v)
            elif isinstance(value, list):
                check.not_empty(prefix)
                for i, v in enumerate(value):
                    rec([*prefix[:-1], f'{prefix[-1]}{self._index_open}{i}{self._index_close}'], v)
            else:
                k = self._delimiter.join(prefix)
                if k in ret:
                    raise KeyError(k)
                ret[k] = value

        ret: dict[str, ta.Any] = {}
        rec([], unflattened)
        return ret

    class UnflattenNode(Abstract, ta.Generic[K]):
        @abc.abstractmethod
        def get(self, key: K) -> ta.Any:
            raise NotImplementedError

        @abc.abstractmethod
        def put(self, key: K, value: ta.Any) -> None:
            raise NotImplementedError

        def setdefault(self, key: K, supplier: ta.Callable[[], V]) -> V:
            ret = self.get(key)
            if ret is ConfigFlattening._MISSING:
                ret = supplier()
                self.put(key, ret)
            return ret

        @abc.abstractmethod
        def build(self) -> ta.Any:
            raise NotImplementedError

        @staticmethod
        def maybe_build(value: ta.Any) -> ta.Any:
            check.not_none(value)
            return value.build() if isinstance(value, ConfigFlattening.UnflattenNode) else value

    class UnflattenDict(UnflattenNode[str]):
        def __init__(self) -> None:
            super().__init__()

            self._dict: dict[str, ta.Any] = {}

        def get(self, key: str) -> ta.Any:
            return self._dict.get(key, ConfigFlattening._MISSING)

        def put(self, key: str, value: ta.Any) -> None:
            check.arg(key not in self._dict)
            self._dict[key] = value

        def build(self) -> ta.Any:
            return {k: ConfigFlattening.UnflattenNode.maybe_build(v) for k, v in self._dict.items()}

    class UnflattenList(UnflattenNode[int]):
        def __init__(self) -> None:
            super().__init__()

            self._list: ta.List[ta.Any] = []

        def get(self, key: int) -> ta.Any:
            check.arg(key >= 0)
            return self._list[key] if key < len(self._list) else ConfigFlattening._MISSING

        def put(self, key: int, value: ta.Any) -> None:
            check.arg(key >= 0)
            if key >= len(self._list):
                self._list.extend([ConfigFlattening._MISSING] * (key - len(self._list) + 1))
            check.arg(self._list[key] is ConfigFlattening._MISSING)
            self._list[key] = value

        def build(self) -> ta.Any:
            return [ConfigFlattening.UnflattenNode.maybe_build(e) for e in self._list]

    def unflatten(self, flattened: ta.Mapping[str, ta.Any]) -> ta.Mapping[str, ta.Any]:
        root = ConfigFlattening.UnflattenDict()

        def split_keys(fkey: str) -> ta.Iterator[ta.Union[str, int]]:
            for part in fkey.split(self._delimiter):
                if self._index_open in part:
                    check.state(part.endswith(self._index_close))
                    pos = part.index(self._index_open)
                    yield part[:pos]
                    for p in part[pos + len(self._index_open):-len(self._index_close)] \
                            .split(self._index_close + self._index_open):
                        yield int(p)
                else:
                    check.state(self._index_close not in part)
                    yield part

        for fk, v in flattened.items():
            node: ConfigFlattening.UnflattenNode = root
            fks = list(split_keys(fk))
            for key, nkey in zip(fks, fks[1:]):  # noqa
                if isinstance(nkey, str):
                    node = node.setdefault(key, ConfigFlattening.UnflattenDict)
                elif isinstance(nkey, int):
                    node = node.setdefault(key, ConfigFlattening.UnflattenList)
                else:
                    raise TypeError(key)
            node.put(fks[-1], v)

        return root.build()
