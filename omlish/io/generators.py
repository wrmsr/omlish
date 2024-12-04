"""
TODO:
 - BufferedBytesGeneratorReader
"""
import typing as ta

from .. import check


class PrependableBytesGeneratorReader:
    def __init__(self) -> None:
        super().__init__()

        self._p: list[bytes] = []

    def read(self, sz: int | None) -> ta.Generator[int | None, bytes, bytes]:
        if not self._p:
            d = check.isinstance((yield sz), bytes)
            return d

        if sz is None:
            return self._p.pop(0)

        l: list[bytes] = []
        r = sz
        while r > 0 and self._p:
            c = self._p[0]

            if len(c) > r:
                l.append(c[:r])
                self._p[0] = c[r:]
                return b''.join(l)

            l.append(c)
            r -= len(c)
            self._p.pop(0)

        if r:
            c = check.isinstance((yield r), bytes)
            if not c:
                return b''
            if len(c) != r:
                raise EOFError(f'Reader got {len(c)} bytes, expected {r}')
            l.append(c)

        return b''.join(l)

    def prepend(self, d: bytes) -> None:
        if d:
            self._p.append(d)
