"""
TODO:
 - \\uXXXX
"""
import re
import typing as ta


_NORMALIZE_PATTERN = re.compile(r'\\([:=\s])')
_ESCAPE_PATTERN = re.compile(r'([=:\s])')
_SEPARATOR_PATTERN = re.compile(r'(?<!\\)[=:]')


def normalize(atom: str) -> str:
    return _NORMALIZE_PATTERN.sub(r'\1', atom.strip())


def escape(token: str) -> str:
    return _ESCAPE_PATTERN.sub(r'\\\1', token)


def parse_line(line: str) -> ta.Optional[ta.Tuple[str, str]]:
    if line and not (line.startswith('#') or line.startswith('!')):
        match = _SEPARATOR_PATTERN.search(line)
        if match:
            return normalize(line[:match.start()]), normalize(line[match.end():])
        else:
            space_sep = line.find(' ')
            if space_sep == -1:
                return normalize(line), ''
            else:
                return normalize(line[:space_sep]), normalize(line[space_sep:])
    return None


def coalesce_lines(lines: ta.Iterable[str]) -> ta.Generator[str, None, None]:
    line_iter = iter(lines)
    try:
        buffer = ''
        while True:
            line = next(line_iter)
            if line.strip().endswith('\\'):
                buffer += line.strip()[:-1]
            else:
                if buffer:
                    buffer += line.rstrip()
                else:
                    buffer = line.strip()
                try:
                    yield buffer
                finally:
                    buffer = ''
    except StopIteration:
        pass


def parse_lines(lines: ta.Iterable[str]) -> ta.Dict[str, str]:
    props = {}
    for line in coalesce_lines(lines):
        kv_pair = parse_line(line)
        if kv_pair:
            key, value = kv_pair
            props[key] = value
    return props
