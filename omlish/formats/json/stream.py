import dataclasses as dc
import io
import re
import typing as ta


TokenKind: ta.TypeAlias = ta.Literal[
    'STRING',
    'NUMBER',

    'SPECIAL_NUMBER',
    'BOOLEAN',
    'NULL',

    'LBRACE',
    'RBRACE',
    'LBRACKET',
    'RBRACKET',
    'COMMA',
    'COLON',
]

TokenValue: ta.TypeAlias = str | float | int | None


class Token(ta.NamedTuple):
    kind: TokenKind
    value: TokenValue
    string: str

    ofs: int
    line: int
    col: int


NUMBER_PAT = re.compile(r'-?(?:0|[1-9]\d*)(?:\.\d+)?(?:[eE][+-]?\d+)?')


PUNCTUATION_TOKENS: ta.Mapping[str, TokenKind] = {
    '{': 'LBRACE',
    '}': 'RBRACE',
    '[': 'LBRACKET',
    ']': 'RBRACKET',
    ',': 'COMMA',
    ':': 'COLON',
}

STATIC_TOKENS: ta.Mapping[str, tuple[TokenKind, str | float | None]] = {
    'NaN': ('SPECIAL_NUMBER', float('nan')),
    'Infinity': ('SPECIAL_NUMBER', float('inf')),
    '-Infinity': ('SPECIAL_NUMBER', float('-inf')),

    'true': ('BOOLEAN', True),
    'false': ('BOOLEAN', False),
    'null': ('NULL', None),
}


@dc.dataclass(frozen=True)
class JsonLexError(Exception):
    message: str

    ofs: int
    line: int
    col: int


def json_stream_lex(it: ta.Iterator[str]) -> ta.Generator[Token, None, None]:
    ofs = 0
    line = 0
    col = 0

    def get_next_char() -> str:
        nonlocal ofs

        try:
            c = next(it)
        except StopIteration:
            raise JsonLexError('Unexpected end of JSON input.', ofs, line, col) from None

        ofs += 1
        return c

    buffer = io.StringIO()

    def flip_buffer() -> str:
        raw = buffer.getvalue()
        buffer.seek(0)
        buffer.truncate()
        return raw

    while True:
        try:
            char = next(it)
        except StopIteration:
            break
        ofs += 1

        if char == '\n':
            line += 1
            col = 0
        else:
            col += 1

        if char.isspace():
            continue

        if char in PUNCTUATION_TOKENS:
            yield Token(PUNCTUATION_TOKENS[char], char, char, ofs, line, col)
            continue

        if char == '"':
            buffer.write(char)
            last = None
            while True:
                char = get_next_char()
                buffer.write(char)
                if char == '"' and last != '\\':
                    break
                last = char

            raw = flip_buffer()
            sv = raw[1:-1].replace(r'\"', '"')
            yield Token('STRING', sv, raw, ofs, line, col)
            continue

        if char.isdigit() or char == '-':
            buffer.write(char)
            while True:
                try:
                    char = get_next_char()
                    if char.isdigit() or char in '.eE+-':
                        buffer.write(char)
                    else:
                        break
                except ValueError:
                    break

            raw = flip_buffer()
            if not NUMBER_PAT.fullmatch(raw):
                raw += char + ''.join(get_next_char() for _ in range(7))
                if raw != '-Infinity':
                    raise JsonLexError(f'Invalid number format: {raw}', ofs, line, col)

                tk, tv = STATIC_TOKENS[raw]
                yield Token(tk, tv, raw, ofs, line, col)
                continue

            nv = float(raw) if '.' in raw or 'e' in raw or 'E' in raw else int(raw)
            yield Token('NUMBER', nv, raw, ofs, line, col)

            if char not in PUNCTUATION_TOKENS and not char.isspace():
                raise JsonLexError(f'Unexpected character after number: {char}', ofs, line, col)

            continue

        if char in 'tfnIN':
            raw = char
            while True:
                raw += get_next_char()
                if raw in STATIC_TOKENS:
                    break

                if len(raw) > 8:  # None of the keywords are longer than 8 characters
                    raise JsonLexError(f'Invalid literal: {raw}', ofs, line, col)

            tk, tv = STATIC_TOKENS[raw]
            yield Token(tk, tv, raw, ofs, line, col)
            continue

        raise JsonLexError(f'Unexpected character: {char}', ofs, line, col)
