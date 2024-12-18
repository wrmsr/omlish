# ruff: noqa: N802 N815
import io
import typing as ta

from .. import check
from . import runtime as antlr4


class DelimitingLexer(antlr4.Lexer):
    def __init__(
            self,
            *args: ta.Any,
            delimiter_token: ta.Any,
            delimiters: ta.Iterable[str],
            no_skip: bool = False,
            **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)

        self._delimiter_token = delimiter_token
        self._delimiters = set(check.not_isinstance(delimiters, str))
        self._no_skip = no_skip

    _hitEOF: bool

    def nextToken(self) -> antlr4.Token:
        if self._input is None:
            raise antlr4.IllegalStateException('nextToken requires a non-null input stream.')

        token_start_marker = self._input.mark()
        try:
            while True:
                if self._hitEOF:
                    self.emitEOF()
                    return self._token

                self._token: antlr4.Token | None = None
                self._channel = antlr4.Token.DEFAULT_CHANNEL
                self._tokenStartCharIndex = self._input.index
                self._tokenStartColumn = self._interp.column
                self._tokenStartLine = self._interp.line
                self._text = None

                continue_outer = False
                while True:
                    self._type = antlr4.Token.INVALID_TYPE
                    ttype = self.SKIP

                    for delimiter in self._delimiters:
                        if self._match_delimiter(delimiter):
                            ttype = self._delimiter_token
                            break
                    else:
                        try:
                            ttype = self._interp.match(self._input, self._mode)
                        except antlr4.LexerNoViableAltException as e:
                            self.notifyListeners(e)  # report error
                            self.recover(e)

                    if self._input.LA(1) == antlr4.Token.EOF:
                        self._hitEOF = True

                    if self._type == antlr4.Token.INVALID_TYPE:
                        self._type = ttype

                    if not self._no_skip and self._type == self.SKIP:
                        continue_outer = True
                        break

                    if self._type != self.MORE:
                        break

                if continue_outer:
                    continue

                if self._token is None:
                    self.emit()

                return self._token

        finally:
            self._input.release(token_start_marker)

    def _match_delimiter(self, delimiter: str) -> bool:
        for i, c in enumerate(delimiter):
            if chr(self._input.LA(i + 1)) != c:
                return False
        self._input.seek(self._input.index + len(delimiter))
        return True

    def split(self) -> tuple[list[tuple[str, str]], str]:
        lst = []
        sb = io.StringIO()
        while True:
            token = self.nextToken()
            if token.type == antlr4.Token.EOF:
                break
            if token.type == self._delimiter_token:
                statement = sb.getvalue().strip()
                if statement:
                    lst.append((statement, token.text))
                sb = io.StringIO()
            else:
                sb.write(token.text)
        partial = sb.getvalue()
        return lst, partial
