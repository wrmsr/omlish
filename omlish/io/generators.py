"""
TODO:
 - BufferedBytesGeneratorReader
 - docstrings
"""
import abc
import typing as ta

from .. import check


T = ta.TypeVar('T')
AnyT = ta.TypeVar('AnyT', bound=ta.Any)


##


class _BytesJoiner:
    def _join(self, lst: list[bytes]) -> bytes:
        return b''.join(lst)


class _StrJoiner:
    def _join(self, lst: list[str]) -> str:
        return ''.join(lst)


##


class GeneratorReader(abc.ABC, ta.Generic[T]):
    @abc.abstractmethod
    def read(self, sz: int | None) -> ta.Generator[int | None, T, T]:
        raise NotImplementedError


##


class PrependableGeneratorReader(GeneratorReader[AnyT]):
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

        lst: list[AnyT] = []
        rem = sz
        while rem > 0 and self._lst:
            c = self._lst[0]

            if len(c) > rem:
                lst.append(c[:rem])
                self._lst[0] = c[rem:]
                return self._join(lst)

            lst.append(c)
            rem -= len(c)
            self._lst.pop(0)

        if rem:
            d = check.not_none((yield rem))
            if not d:
                return self._join([])  # type: ignore[unreachable]
            if len(d) != rem:  # type: ignore[unreachable]
                raise EOFError(f'Reader got {len(d)}, expected {rem}')
            lst.append(d)

        if len(lst) == 1:
            return lst[0]
        else:
            return self._join(lst)

    def prepend(self, d: AnyT) -> None:
        if d:
            self._lst.append(d)


class PrependableBytesGeneratorReader(
    _BytesJoiner,
    PrependableGeneratorReader[bytes],
):
    pass


class PrependableStrGeneratorReader(
    _StrJoiner,
    PrependableGeneratorReader[str],
):
    pass


##


class BufferedGeneratorReader(PrependableGeneratorReader[AnyT], abc.ABC):
    DEFAULT_BUFFER_SIZE = 4 * 0x1000

    def __init__(
            self,
            buffer_size: int = DEFAULT_BUFFER_SIZE,
    ) -> None:
        check.arg(buffer_size > 0)

        super().__init__()

        self._buffer_size = buffer_size

    def read(self, sz: int | None) -> ta.Generator[int | None, AnyT, AnyT]:
        return super().read(sz)


class BufferedBytesGeneratorReader(
    _BytesJoiner,
    BufferedGeneratorReader[bytes],
    PrependableGeneratorReader[bytes],
):
    pass


class BufferedStrGeneratorReader(
    _StrJoiner,
    BufferedGeneratorReader[str],
    PrependableGeneratorReader[str],
):
    pass
