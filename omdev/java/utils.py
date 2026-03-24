import re


##


_LINE_RE = re.compile(r'.*?(?:\r\n|\n|\r|$)')


def insert_before_first_non_header_line(java_src: str, new_line: str) -> str:
    """
    Insert `new_line` as its own line immediately before the first non-header line in `java_src`.

    A "header" line is:
      - blank / whitespace-only
      - a `// ...` line (optionally indented)
      - a `/* ... */` block-comment line, including multi-line block comments (optionally indented)

    Assumptions:
      - `java_src` contains valid Java source.
      - If a line ends a block comment, it does not also contain code after `*/`.
      - `new_line` is a single logical line; any trailing newline chars are ignored.
    """

    # Pick a newline style to use for the inserted line.
    m = re.search(r'\r\n|\n|\r', java_src)
    nl = m.group(0) if m else '\n'

    in_block_comment = False

    for m in _LINE_RE.finditer(java_src):
        line = m.group(0)
        if line == '':
            break

        stripped = line.lstrip()

        if in_block_comment:
            if '*/' in stripped:
                in_block_comment = False
            continue

        if stripped == '' or stripped in ('\n', '\r', '\r\n'):
            continue

        if stripped.startswith('//'):
            continue

        if stripped.startswith('/*'):
            if '*/' not in stripped:
                in_block_comment = True
            continue

        # First non-header line.
        return java_src[:m.start()] + new_line + nl + java_src[m.start():]

    # File contains only header lines, or is empty: append at the end.
    if not java_src:
        return new_line + nl

    return java_src + ('' if java_src.endswith(('\r\n', '\n', '\r')) else nl) + new_line + nl
