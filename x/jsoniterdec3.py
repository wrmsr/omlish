import re
import typing as ta


# Define token types
Token: ta.TypeAlias = tuple[str, str | float | int | None]

# Regex patterns for different JSON tokens
STRING_REGEX = re.compile(r'"(?:\\.|[^"\\])*"')
NUMBER_REGEX = re.compile(r'-?(?:0|[1-9]\d*)(?:\.\d+)?(?:[eE][+-]?\d+)?')
TRUE_REGEX = re.compile(r'true')
FALSE_REGEX = re.compile(r'false')
NULL_REGEX = re.compile(r'null')

# Define token constants
PUNCTUATION_TOKENS: ta.Mapping[str, str] = {
    '{': 'LBRACE',
    '}': 'RBRACE',
    '[': 'LBRACKET',
    ']': 'RBRACKET',
    ',': 'COMMA',
    ':': 'COLON'
}


# Function to yield tokens
def json_lexer(char_iter: ta.Iterator[str]) -> ta.Generator[Token, None, None]:
    buffer: str

    def get_next_char() -> str:
        """Get the next character from the iterator, or raise an error if exhausted."""
        try:
            return next(char_iter)
        except StopIteration:
            raise ValueError("Unexpected end of JSON input.")

    while True:
        char = get_next_char()

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
            if not NUMBER_REGEX.fullmatch(buffer):
                raise ValueError(f"Invalid number format: {buffer}")
            yield ('NUMBER', float(buffer) if '.' in buffer or 'e' in buffer or 'E' in buffer else int(buffer))
            if char not in PUNCTUATION_TOKENS and not char.isspace():
                raise ValueError(f"Unexpected character after number: {char}")
            continue

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


if __name__ == "__main__":
    # json_input = '{"name": "John", "age": 30, "active": true, "scores": [85, 90, 88], "address": null}'

    import json
    import yaml
    with open('x/llm/openai/api.yaml') as f:
        json_input = json.dumps(yaml.safe_load(f))

    char_iter = iter(json_input)

    try:
        for token in json_lexer(char_iter):
            print(token)
    except ValueError as e:
        print(f"Error: {e}")
