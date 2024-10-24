import re
from typing import Generator, Tuple, Union, Iterator

# Define token types
Token = Tuple[str, Union[str, float, int, None]]
TokenType = str

# Regex patterns for different JSON tokens
STRING_REGEX = re.compile(r'"(?:\\.|[^"\\])*"')
NUMBER_REGEX = re.compile(r'-?(?:0|[1-9]\d*)(?:\.\d+)?(?:[eE][+-]?\d+)?')

# Define token constants
PUNCTUATION_TOKENS = {
    '{': 'LBRACE',
    '}': 'RBRACE',
    '[': 'LBRACKET',
    ']': 'RBRACKET',
    ',': 'COMMA',
    ':': 'COLON'
}

SPECIAL_NUMBER_TOKENS = {'NaN', 'Infinity', '-Infinity'}

# Function to yield tokens
def json_lexer(char_iter: Iterator[str]) -> Generator[Token, None, None]:
    buffer = ""

    def get_next_char() -> str:
        """Get the next character from the iterator, or raise an error if exhausted."""
        try:
            return next(char_iter)
        except StopIteration:
            raise ValueError("Unexpected end of JSON input.")

    while True:
        try:
            char = next(char_iter)
        except StopIteration:
            break

        # Skip whitespace characters
        if char.isspace():
            continue

        # Handle punctuation tokens
        if char in PUNCTUATION_TOKENS:
            yield (PUNCTUATION_TOKENS[char], char)
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

        # Handle number tokens (including NaN, Infinity, -Infinity)
        if char.isdigit() or char in '-nI':
            buffer = char
            while True:
                try:
                    char = get_next_char()
                    if char.isdigit() or char in '.eE+-':
                        buffer += char
                    elif buffer in SPECIAL_NUMBER_TOKENS:
                        break
                    else:
                        if char.isalpha():
                            buffer += char
                        else:
                            break
                except ValueError:
                    break

            # Match special numbers: NaN, Infinity, -Infinity
            if buffer in SPECIAL_NUMBER_TOKENS:
                yield ('NUMBER', float(buffer))
                if char not in PUNCTUATION_TOKENS and not char.isspace():
                    raise ValueError(f"Unexpected character after special number: {char}")
                continue

            # Match regular numbers
            if NUMBER_REGEX.fullmatch(buffer):
                yield ('NUMBER', float(buffer) if '.' in buffer or 'e' in buffer or 'E' in buffer else int(buffer))
                if char not in PUNCTUATION_TOKENS and not char.isspace():
                    raise ValueError(f"Unexpected character after number: {char}")
                continue

            # If "null" was incorrectly detected as a number, ignore that and proceed
            if buffer == 'null':
                yield ('NULL', None)
                continue

            raise ValueError(f"Invalid number format: {buffer}")

        # Handle true, false, and null
        if char in 'tfn':
            buffer = char
            while True:
                buffer += get_next_char()
                if buffer in ('true', 'false', 'null'):
                    break
                if len(buffer) > 5:  # None of the keywords are longer than 5 characters
                    raise ValueError(f"Invalid literal: {buffer}")

            if buffer == 'true':
                yield ('BOOLEAN', True)
            elif buffer == 'false':
                yield ('BOOLEAN', False)
            elif buffer == 'null':
                yield ('NULL', None)
            continue

        # If we reach here, we found an unexpected character
        raise ValueError(f"Unexpected character: {char}")
def _main() -> None:
    import json
    import yaml
    with open('x/llm/openai/api.yaml') as f:
        big_json_input = json.dumps(yaml.safe_load(f))

    for s in [
        '{"name": "John", "age": 30, "active": true, "scores": [85, 90, 88], "address": null}',
        '{"name": "John", "age": NaN, "score": Infinity, "loss": -Infinity, "active": true}',
        big_json_input,
    ]:
        try:
            for token in json_lexer(iter(s)):
                print(token)
        except ValueError as e:
            print(f'Error: {e}')


if __name__ == '__main__':
    _main()
