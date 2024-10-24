import re
import typing as ta


# Define token types
Token = tuple[str, str | float | int | None]
TokenType = str


# Regex patterns for different JSON tokens
TOKEN_REGEX = {
    'WHITESPACE': r'\s+',
    'LBRACE': r'\{',
    'RBRACE': r'\}',
    'LBRACKET': r'\[',
    'RBRACKET': r'\]',
    'COMMA': r',',
    'COLON': r':',
    'STRING': r'"(?:\\.|[^"\\])*"',  # Supports escaped characters
    'NUMBER': r'-?(?:0|[1-9]\d*)(?:\.\d+)?(?:[eE][+-]?\d+)?',
    'TRUE': r'true',
    'FALSE': r'false',
    'NULL': r'null',
}

# Compile the regex patterns into one master pattern
MASTER_PATTERN = re.compile('|'.join(
    f'(?P<{name}>{pattern})'
    for name, pattern in TOKEN_REGEX.items()
))


# Function to yield tokens
def json_lexer(json_string: str) -> ta.Generator[Token, None, None]:
    pos = 0
    length = len(json_string)

    while pos < length:
        match = MASTER_PATTERN.match(json_string, pos)
        if not match:
            raise ValueError(f"Unexpected character at position {pos}: '{json_string[pos]}'")

        token_type = match.lastgroup
        token_value = match.group(token_type)

        # Skip whitespace tokens
        if token_type == 'WHITESPACE':
            pos = match.end()
            continue

        # Process each token type and yield the appropriate token
        if token_type == 'STRING':
            yield ('STRING', token_value[1:-1].replace('\\"', '"'))  # Strip quotes and unescape

        elif token_type == 'NUMBER':
            if '.' in token_value or 'e' in token_value or 'E' in token_value:
                yield ('NUMBER', float(token_value))
            else:
                yield ('NUMBER', int(token_value))

        elif token_type == 'TRUE':
            yield ('BOOLEAN', True)

        elif token_type == 'FALSE':
            yield ('BOOLEAN', False)

        elif token_type == 'NULL':
            yield ('NULL', None)

        else:
            # For punctuation tokens like braces, brackets, commas, and colons
            yield (token_type, token_value)

        # Move the position to the end of the matched token
        pos = match.end()


if __name__ == "__main__":
    # json_input = """{"name": "John Doe", "age": 30, "is_active": true, "hobbies": ["reading", "gaming"], "balance": 1234.56, "spouse": null}"""

    import json
    import yaml
    with open('x/llm/openai/api.yaml') as f:
        json_input = json.dumps(yaml.safe_load(f))

    # Tokenize the JSON string
    for token in json_lexer(json_input):
        print(token)
