"""
TODO:
 - BufferedBytesGeneratorReader
 - docstrings
 - memoryviews
"""
import abc
import typing as ta

from ... import check
from .consts import DEFAULT_BUFFER_SIZE


T = ta.TypeVar('T')

O = ta.TypeVar('O')
I = ta.TypeVar('I')
R = ta.TypeVar('R')

AnyT = ta.TypeVar('AnyT', bound=ta.Any)


# Reader generators yield ints of amounts of data needed, or None for needing any amount of data.
ReaderGenerator: ta.TypeAlias = ta.Generator[int | None, I, R]

BytesReaderGenerator: ta.TypeAlias = ReaderGenerator[bytes, R]
StrReaderGenerator: ta.TypeAlias = ReaderGenerator[str, R]


# Exact reader generators always specify read sizes.
ExactReaderGenerator: ta.TypeAlias = ta.Generator[int, I, R]

BytesExactReaderGenerator: ta.TypeAlias = ExactReaderGenerator[bytes, R]
StrExactReaderGenerator: ta.TypeAlias = ExactReaderGenerator[str, R]


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
    def read(self, sz: int | None) -> ReaderGenerator[T, T]:
        raise NotImplementedError

    def read_exact(self, sz: int) -> ReaderGenerator[T, T]:
        d: ta.Any = yield from self.read(sz)
        if len(d) != sz:
            raise EOFError(f'GeneratorReader got {len(d)}, expected {sz}')
        return d


##


class PrependableGeneratorReader(GeneratorReader[AnyT]):
    def __init__(self) -> None:
        super().__init__()

        self._queue: list[tuple[AnyT, int]] = []

    @abc.abstractmethod
    def _join(self, lst: list[AnyT]) -> AnyT:
        raise NotImplementedError

    def read(self, sz: int | None) -> ReaderGenerator[AnyT, AnyT]:
        if not self._queue:
            d: AnyT = check.not_none((yield sz))
            return d

        if sz is None:
            return self._queue.pop(0)[0]

        lst: list[AnyT] = []
        rem = sz
        while rem > 0 and self._queue:
            c, p = self._queue[0]

            if len(c) - p > rem:
                lst.append(c[p:p + rem])
                self._queue[0] = (c, p + rem)
                return self._join(lst)

            lst.append(c[p:])
            rem -= len(c) - p
            self._queue.pop(0)

        if rem:
            d = check.not_none((yield rem))
            if d:
                lst.append(d)  # type: ignore[unreachable]

        if len(lst) == 1:
            return lst[0]
        else:
            return self._join(lst)

    def prepend(self, d: AnyT, p: int | None = None) -> None:
        if d:
            self._queue.insert(0, (d, p or 0))


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


prependable_bytes_generator_reader = PrependableBytesGeneratorReader
prependable_str_generator_reader = PrependableStrGeneratorReader


##


class BufferedGeneratorReader(PrependableGeneratorReader[AnyT], abc.ABC):
    def __init__(
            self,
            buffer_size: int = DEFAULT_BUFFER_SIZE,
    ) -> None:
        check.arg(buffer_size > 0)

        super().__init__()

        self._buffer_size = buffer_size

    def read(self, sz: int | None) -> ReaderGenerator[AnyT, AnyT]:
        g = super().read(sz)
        i: ta.Any = None
        while True:
            try:
                q = g.send(i)
            except StopIteration as e:
                return e.value

            check.state(not self._queue)

            if q is None:
                i = check.not_none((yield None))
                continue

            r = max(q, self._buffer_size)
            d: AnyT = check.not_none((yield r))
            if len(d) < q:
                i = d
                continue

            i = d[:q]
            self.prepend(d, q)


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


buffered_bytes_generator_reader = BufferedBytesGeneratorReader
buffered_str_generator_reader = BufferedStrGeneratorReader
