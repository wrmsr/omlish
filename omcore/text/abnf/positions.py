##


def get_ofs_line_column(s: str, p: int) -> tuple[int, int]:
    """
    Returns the 0-based (line, column) position of offset `p` in `s`. `p == len(s)` - one past the final character - is
    permitted, denoting the end of the source.
    """

    if not (0 <= p <= len(s)):
        raise ValueError(f'Offset {p} out of range for string of length {len(s)}')

    r = p
    n = 0
    for l in s.splitlines(keepends=True):
        if r < len(l) or (r == len(l) and not l.endswith(('\n', '\r'))):
            return (n, r)
        r -= len(l)
        n += 1
    return (n, r)


def format_offset(s: str, p: int) -> str:
    """Renders offset `p` in `s` as a human-readable, 1-based 'line X, column Y' string."""

    l, c = get_ofs_line_column(s, p)
    return f'line {l + 1}, column {c + 1}'
