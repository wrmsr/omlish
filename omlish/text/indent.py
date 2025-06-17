# ruff: noqa: UP006 UP007 UP045
# @omlish-lite
import contextlib
import io
import typing as ta

from ..lite.check import check


##


class IndentWriter:
    DEFAULT_INDENT: ta.ClassVar[str] = ' ' * 4

    def __init__(
            self,
            *,
            buf: ta.Optional[io.StringIO] = None,
            indent: ta.Optional[str] = None,
    ) -> None:
        super().__init__()

        self._buf = buf if buf is not None else io.StringIO()
        self._indent = check.isinstance(indent, str) if indent is not None else self.DEFAULT_INDENT
        self._level = 0
        self._cache: ta.Dict[int, str] = {}
        self._has_indented = False

    @contextlib.contextmanager
    def indent(self, num: int = 1) -> ta.Iterator[None]:
        self._level += num
        try:
            yield
        finally:
            self._level -= num

    def write(self, s: str) -> None:
        try:
            indent = self._cache[self._level]
        except KeyError:
            indent = self._cache[self._level] = self._indent * self._level
        i = 0
        while i < len(s):
            if not self._has_indented:
                self._buf.write(indent)
                self._has_indented = True
            try:
                n = s.index('\n', i)
            except ValueError:
                self._buf.write(s[i:])
                break
            self._buf.write(s[i:n + 1])
            self._has_indented = False
            i = n + 2

    def getvalue(self) -> str:
        return self._buf.getvalue()
