"""
TODO:
 - BufferedBytesGeneratorReader
"""
import abc
import typing as ta

from .. import check


AnyT = ta.TypeVar('AnyT', bound=ta.Any)


class PrependableGeneratorReader(ta.Generic[AnyT]):
    def __init__(self) -> None:
        super().__init__()

        self._lst: list[AnyT] = []

    @abc.abstractmethod
    def _join(self, lst: list[AnyT]) -> AnyT:
        raise NotImplementedError

    def read(self, sz: int | None) -> ta.Generator[int | None, AnyT, AnyT]:
        if not self._lst:
            d: AnyT = check.not_none((yield sz))
            return d

        if sz is None:
            return self._lst.pop(0)

        l: list[AnyT] = []
        r = sz
        while r > 0 and self._lst:
            c = self._lst[0]

            if len(c) > r:
                l.append(c[:r])
                self._lst[0] = c[r:]
                return self._join(l)

            l.append(c)
            r -= len(c)
            self._lst.pop(0)

        if r:
            d = check.not_none((yield r))
            if not d:
                return self._join([])  # type: ignore[unreachable]
            if len(d) != r:  # type: ignore[unreachable]
                raise EOFError(f'Reader got {len(d)}, expected {r}')
            l.append(d)

        if len(l) == 1:
            return l[0]
        else:
            return self._join(l)

    def prepend(self, d: AnyT) -> None:
        if d:
            self._lst.append(d)


class PrependableBytesGeneratorReader(PrependableGeneratorReader[bytes]):
    def _join(self, lst: list[bytes]) -> bytes:
        return b''.join(lst)


class PrependableStrGeneratorReader(PrependableGeneratorReader[str]):
    def _join(self, lst: list[str]) -> str:
        return ''.join(lst)
