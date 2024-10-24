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

Token: ta.TypeAlias = tuple[TokenKind, str | float | int | None]

NUMBER_PAT = re.compile(r'-?(?:0|[1-9]\d*)(?:\.\d+)?(?:[eE][+-]?\d+)?')

PUNCTUATION_TOKENS: ta.Mapping[str, Token] = {
    '{': ('LBRACE', '{'),
    '}': ('RBRACE', '}'),
    '[': ('LBRACKET', '['),
    ']': ('RBRACKET', ']'),
    ',': ('COMMA', ','),
    ':': ('COLON', ':'),
}

STATIC_TOKENS: ta.Mapping[str, Token] = {
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

        nonlocal pos
        pos += 1
        return c

    buffer: str
    pos = 0
    while True:
        try:
            char = next(it)
        except StopIteration:
            break
        pos += 1

        # Skip whitespace characters
        if char.isspace():
            continue

        # Handle punctuation tokens
        if char in PUNCTUATION_TOKENS:
            yield PUNCTUATION_TOKENS[char]
            continue

        # Handle string tokens
        if char == '"':
            buffer = char
            while True:
                char = get_next_char()
                buffer += char
                if char == '"' and not buffer.endswith(r'\"'):
                    break

            yield ('STRING', buffer[1:-1].replace(r'\"', '"'))
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
                raise ValueError(f'Invalid number format: {buffer}')

            yield ('NUMBER', float(buffer) if '.' in buffer or 'e' in buffer or 'E' in buffer else int(buffer))

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

            yield STATIC_TOKENS[buffer]
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
        # '{"name": "John", "age": NaN, "score": Infinity, "loss": -Infinity, "active": true, "foo": null}',
        big_json_input,
    ]:
        for token in json_lexer(iter(s)):
            print(token)


if __name__ == '__main__':
    _main()
