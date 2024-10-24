import re
import typing as ta


# Define token types
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
    offset: int

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


# Function to yield tokens
def json_lexer(it: ta.Iterator[str]) -> ta.Generator[Token, None, None]:
    def get_next_char() -> str:
        """Get the next character from the iterator, or raise an error if exhausted."""

        try:
            c = next(it)
        except StopIteration:
            raise ValueError('Unexpected end of JSON input.')  # noqa

        nonlocal offset
        offset += 1
        return c

    buffer: str
    offset = 0
    while True:
        try:
            char = next(it)
        except StopIteration:
            break
        offset += 1

        # Skip whitespace characters
        if char.isspace():
            continue

        # Handle punctuation tokens
        if char in PUNCTUATION_TOKENS:
            yield Token(
                PUNCTUATION_TOKENS[char],
                char,
                char,
                offset,
            )
            continue

        # Handle string tokens
        if char == '"':
            buffer = char
            while True:
                char = get_next_char()
                buffer += char
                if char == '"' and not buffer.endswith(r'\"'):
                    break

            yield Token(
                'STRING',
                buffer[1:-1].replace(r'\"', '"'),
                buffer,
                offset,
            )
            continue

        # Handle number tokens
        if char.isdigit() or char == '-':
            buffer = char
            while True:
                try:
                    char = get_next_char()
                    if char.isdigit() or char in '.eE+-':
                        buffer += char
                    else:
                        break
                except ValueError:
                    break

            if not NUMBER_PAT.fullmatch(buffer):
                buffer += char + ''.join(get_next_char() for _ in range(7))
                if buffer != '-Infinity':
                    raise ValueError(f'Invalid number format: {buffer}')

                tk, tv = STATIC_TOKENS[buffer]
                yield Token(
                    tk,
                    tv,
                    buffer,
                    offset
                )
                continue

            yield Token(
                'NUMBER',
                float(buffer) if '.' in buffer or 'e' in buffer or 'E' in buffer else int(buffer),
                buffer,
                offset,
            )

            if char not in PUNCTUATION_TOKENS and not char.isspace():
                raise ValueError(f'Unexpected character after number: {char}')

            continue

        if char in 'tfnIN':
            buffer = char
            while True:
                buffer += get_next_char()
                if buffer in STATIC_TOKENS:
                    break

                if len(buffer) > 8:  # None of the keywords are longer than 8 characters
                    raise ValueError(f'Invalid literal: {buffer}')

            tk, tv = STATIC_TOKENS[buffer]
            yield Token(
                tk,
                tv,
                buffer,
                offset,
            )
            continue

        # If we reach here, we found an unexpected character
        raise ValueError(f'Unexpected character: {char}')


def _main() -> None:
    import json
    import yaml
    with open('x/llm/openai/api.yaml') as f:
        big_json_input = json.dumps(yaml.safe_load(f))

    for s in [
        '{"name": "John", "age": 30, "active": true, "scores": [85, 90, 88], "address": null}',
        '{"name": "John", "age": NaN, "score": Infinity, "active": true, "foo": null}',
        '{"name": "John", "age": NaN, "score": Infinity, "loss": -Infinity, "active": true, "foo": null}',
        big_json_input,
    ]:
        for token in json_lexer(iter(s)):
            print(token)


if __name__ == '__main__':
    _main()
