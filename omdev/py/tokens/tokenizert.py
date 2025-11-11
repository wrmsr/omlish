# @omlish-lite
# ruff: noqa: UP006 UP007 UP045
# Copyright (c) 2017 Anthony Sottile
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the "Software"), to deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit
# persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the
# Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
# https://github.com/asottile/tokenize-rt/blob/d3874b787677593fc34aedf7174a2934e2caa94b/tokenize_rt.py
import argparse
import io
import keyword
import re
import tokenize
import typing as ta

from omlish.lite.check import check


##


class TokenNames:
    def __new__(cls, *args, **kwargs):  # noqa
        raise TypeError

    ESCAPED_NL = 'ESCAPED_NL'
    UNIMPORTANT_WS = 'UNIMPORTANT_WS'
    NON_CODING_TOKENS = frozenset(('COMMENT', ESCAPED_NL, 'NL', UNIMPORTANT_WS))


class TokenOffset(ta.NamedTuple):
    line: ta.Optional[int] = None
    utf8_byte_offset: ta.Optional[int] = None


class Token(ta.NamedTuple):
    name: str
    src: str
    line: ta.Optional[int] = None
    utf8_byte_offset: ta.Optional[int] = None

    @property
    def offset(self) -> TokenOffset:
        return TokenOffset(self.line, self.utf8_byte_offset)

    def matches(self, *, name: str, src: str) -> bool:
        return self.name == name and self.src == src


##


class Tokenization:
    _STRING_RE = re.compile('^([^\'"]*)(.*)$', re.DOTALL)
    _ESCAPED_NL_RE = re.compile(r'\\(\n|\r\n|\r)')

    _NAMED_UNICODE_RE = re.compile(r'(?<!\\)(?:\\\\)*(\\N\{[^}]+\})')

    @classmethod
    def curly_escape(cls, s: str) -> str:
        parts = cls._NAMED_UNICODE_RE.split(s)
        return ''.join(
            part.replace('{', '{{').replace('}', '}}') if i % 2 == 0 else part
            for i, part in enumerate(parts)
        )

    @classmethod
    def _re_partition(cls, regex: ta.Pattern[str], s: str) -> ta.Tuple[str, str, str]:
        match = regex.search(s)
        if match:
            return s[:match.start()], s[slice(*match.span())], s[match.end():]
        else:
            return (s, '', '')

    @classmethod
    def iter_src_to_tokens(cls, src: str) -> ta.Iterator[Token]:
        tokenize_target = io.StringIO(src)
        lines = ('', *tokenize_target)

        tokenize_target.seek(0)

        last_line = 1
        last_col = 0
        end_offset = 0

        gen = tokenize.generate_tokens(tokenize_target.readline)
        for tok_type, tok_text, (sline, scol), (eline, ecol), line in gen:
            if sline > last_line:
                newtok = lines[last_line][last_col:]
                for lineno in range(last_line + 1, sline):
                    newtok += lines[lineno]
                if scol > 0:
                    newtok += lines[sline][:scol]

                # a multiline unimportant whitespace may contain escaped newlines
                while cls._ESCAPED_NL_RE.search(newtok):
                    ws, nl, newtok = cls._re_partition(cls._ESCAPED_NL_RE, newtok)
                    if ws:
                        yield Token(TokenNames.UNIMPORTANT_WS, ws, last_line, end_offset)
                        end_offset += len(ws.encode())
                    yield Token(TokenNames.ESCAPED_NL, nl, last_line, end_offset)
                    end_offset = 0
                    last_line += 1
                if newtok:
                    yield Token(TokenNames.UNIMPORTANT_WS, newtok, sline, 0)
                    end_offset = len(newtok.encode())
                else:
                    end_offset = 0

            elif scol > last_col:
                newtok = line[last_col:scol]
                yield Token(TokenNames.UNIMPORTANT_WS, newtok, sline, end_offset)
                end_offset += len(newtok.encode())

            tok_name = tokenize.tok_name[tok_type]

            if tok_name in {'FSTRING_MIDDLE', 'TSTRING_MIDDLE'}:  # pragma: >=3.12 cover
                if '{' in tok_text or '}' in tok_text:
                    new_tok_text = cls.curly_escape(tok_text)
                    ecol += len(new_tok_text) - len(tok_text)
                    tok_text = new_tok_text

            yield Token(tok_name, tok_text, sline, end_offset)
            last_line, last_col = eline, ecol
            if sline != eline:
                end_offset = len(lines[last_line][:last_col].encode())
            else:
                end_offset += len(tok_text.encode())

    @classmethod
    def src_to_tokens(cls, src: str) -> ta.List[Token]:
        return list(cls.iter_src_to_tokens(src))

    @classmethod
    def parse_string_literal(cls, src: str) -> ta.Tuple[str, str]:
        """parse a string literal's source into (prefix, string)"""
        match = check.not_none(cls._STRING_RE.match(src))
        return match.group(1), match.group(2)

    @classmethod
    def tokens_to_src(cls, tokens: ta.Iterable[Token]) -> str:
        return ''.join(tok.src for tok in tokens)

    @classmethod
    def rfind_string_parts(cls, tokens: ta.Sequence[Token], start: int) -> ta.Tuple[int, ...]:
        """
        Find the indicies of the string parts of a (joined) string literal.

        - `i` should start at the end of the string literal
        - returns `()` (an empty tuple) for things which are not string literals
        """

        ret = []
        depth = 0
        for i in range(start, -1, -1):
            token = tokens[i]
            if token.name == 'STRING':
                ret.append(i)
            elif token.name in TokenNames.NON_CODING_TOKENS:
                pass
            elif token.src == ')':
                depth += 1
            elif depth and token.src == '(':
                depth -= 1
                # if we closed the paren(s) make sure it was a parenthesized string
                # and not actually a call
                if depth == 0:
                    for j in range(i - 1, -1, -1):
                        tok = tokens[j]
                        if tok.name in TokenNames.NON_CODING_TOKENS:
                            pass
                        # this was actually a call and not a parenthesized string
                        elif (
                                tok.src in {']', ')'} or (
                                    tok.name == 'NAME' and
                                    tok.src not in keyword.kwlist
                                )
                        ):
                            return ()
                        else:
                            break
                    break
            elif depth:  # it looked like a string but wasn't
                return ()
            else:
                break
        return tuple(reversed(ret))


##


if __name__ == '__main__':
    def main(argv: ta.Optional[ta.Sequence[str]] = None) -> int:
        parser = argparse.ArgumentParser()
        parser.add_argument('filename')
        args = parser.parse_args(argv)
        with open(args.filename) as f:
            tokens = Tokenization.src_to_tokens(f.read())

        for token in tokens:
            line, col = str(token.line), str(token.utf8_byte_offset)
            print(f'{line}:{col} {token.name} {token.src!r}')

        return 0

    raise SystemExit(main())
