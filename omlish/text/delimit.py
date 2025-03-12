"""
TODO:
 - replace with codecs.StreamReader
"""
import io
import typing as ta


class DelimitedEscaping:
    def __init__(
            self,
            delimit_char: str,
            quote_char: str,
            escape_char: str,
            escaped_chars: ta.Iterable[str] = (),
    ) -> None:
        super().__init__()

        self._delimit_char = delimit_char
        self._quote_char = quote_char
        self._escape_char = escape_char
        self._escaped_chars = frozenset(escaped_chars)

        for c in [delimit_char, quote_char, escape_char]:
            if not isinstance(c, str) or len(c) != 1:
                raise TypeError(c)
        for c in self._escaped_chars:
            if not isinstance(c, str):
                raise TypeError(c)

        self._all_escaped_chars = frozenset({delimit_char, quote_char, escape_char} | self._escaped_chars)

    @property
    def delimit_char(self) -> str:
        return self._delimit_char

    def quote_char(self) -> str:
        return self._quote_char

    def escape_char(self) -> str:
        return self._escape_char

    def escaped_chars(self) -> frozenset[str]:
        return self._escaped_chars

    def all_escaped_chars(self) -> frozenset[str]:
        return self._all_escaped_chars

    def is_control_char(self, c: str) -> bool:
        if not len(c) == 1:
            raise TypeError(c)
        return c == self._delimit_char or c == self._quote_char or c == self._escape_char  # noqa

    def contains_escaped_char(self, s: str) -> bool:
        return any(c in self._all_escaped_chars for c in s)

    def escape(self, s: str) -> str:
        buf = io.StringIO()
        for c in s:
            if c in self._all_escaped_chars:
                buf.write(self._escape_char)
            buf.write(c)
        return buf.getvalue()

    def unescape(self, s: str) -> str:
        buf = io.StringIO()
        i = 0
        while i < len(s):
            c = s[i]
            if c == self._escape_char:
                if i > (len(s) - 2):
                    raise ValueError(s)
                i += 1
                buf.write(s[i])
            else:
                if c in self._all_escaped_chars:
                    raise ValueError(s)
                buf.write(c)
            i += 1
        return buf.getvalue()

    def quote(self, s: str) -> str:
        if self.contains_escaped_char(s):
            return self._quote_char + self.escape(s) + self._quote_char
        else:
            return s

    def unquote(self, s: str) -> str:
        if s and s[0] == self._quote_char:
            if len(s) < 2 or s[-1] != self._quote_char:
                raise ValueError(s)
            return self.unescape(s[1:-1])
        else:
            return s

    def delimit_many(self, strs: ta.Iterable[str]) -> str:
        if isinstance(strs, str):
            raise TypeError(strs)
        buf = io.StringIO()
        for count, s in enumerate(strs):
            if count:
                buf.write(self._delimit_char)
            if self.contains_escaped_char(s):
                buf.write(self.quote(s))
            else:
                buf.write(s)
        return buf.getvalue()

    def delimit(self, s: str) -> str:
        if not isinstance(s, str):
            raise TypeError(s)
        return self.delimit_many([s])

    def undelimit(self, s: str) -> list[str]:
        ret = []
        buf = io.StringIO()
        count = 0
        i = 0

        while i < len(s):
            c = s[i]

            if count:
                if c != self._delimit_char or i >= (len(s) - 1):
                    raise ValueError(s)
                i += 1
                c = s[i]

            quoted = c == self._quote_char
            if quoted:
                if i >= (len(s) - 1):
                    raise ValueError(s)
                i += 1
                c = s[i]
            unquoted = False

            while True:
                if c == self._delimit_char:
                    if not quoted:
                        break
                    buf.write(c)
                elif c == self._quote_char:
                    if not quoted:
                        raise ValueError(s)
                    unquoted = True
                    i += 1
                    break
                elif c == self._escape_char:
                    if not quoted or i > (len(s) - 2):
                        raise ValueError(s)
                    i += 1
                    buf.write(s[i])
                else:
                    if c in self._escaped_chars:
                        raise ValueError(s)
                    buf.write(c)

                i += 1
                if i == len(s):
                    break
                c = s[i]

            if quoted and not unquoted:
                raise ValueError(s)

            ret.append(buf.getvalue())
            buf.seek(0)
            buf.truncate()
            count += 1

        return ret
