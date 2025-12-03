def textwrap_repr(text: str, width: int = 120, quote_char: str = '"') -> list[str]:
    escaped_quote = '\\' + quote_char
    content_width = width - 2

    lines: list[str] = []
    current_line: list[str] = []
    current_length = 0

    for char in text:
        if char == quote_char:
            safe_char = escaped_quote
        elif char == '\\':
            safe_char = '\\\\'
        elif not char.isprintable():
            safe_char = repr(char)[1:-1]
            if quote_char in safe_char:
                safe_char = safe_char.replace(quote_char, escaped_quote)
        else:
            safe_char = char

        if current_length + len(safe_char) > content_width:
            lines.append(f"{quote_char}{''.join(current_line)}{quote_char}")
            current_line = []
            current_length = 0

        current_line.append(safe_char)
        current_length += len(safe_char)

    if current_line:
        lines.append(f"{quote_char}{''.join(current_line)}{quote_char}")

    return lines
