"""
https://github.com/kojiromike/parameter_expansion/blob/master/pe.py
"""
import typing as ta

from .. import check


r"""
_ESCAPE_DECODER = codecs.getdecoder('unicode_escape')
_POSIX_VARIABLE = re.compile('\$\{[^\}]*\}')


def decode_escaped(escaped):
    return _ESCAPE_DECODER(escaped)[0]


def parse_line(line):
    line = line.strip()

    # Ignore lines with `#` or which doesn't have `=` in it.
    if not line or line.startswith('#') or '=' not in line:
        return None, None

    k, v = line.split('=', 1)

    if k.startswith('export '):
        (_, _, k) = k.partition('export ')

    # Remove any leading and trailing spaces in key, value
    k, v = k.strip(), v.strip()

    if v:
        v = v.encode('unicode-escape').decode('ascii')
        quoted = v[0] == v[-1] in ['"', "'"]
        if quoted:
            v = decode_escaped(v[1:-1])

    return k, v


def resolve_nested_variables(values):
    def replacement(name):
        ret = os.getenv(name, values.get(name, ""))
        return ret

    def re_sub_callback(match_object):
        return replacement(match_object.group()[2:-1])

    for k, v in values.items():
        values[k] = _POSIX_VARIABLE.sub(re_sub_callback, v)

    return values
"""


def dumb_parse_lines(lines: ta.Iterable[str]) -> ta.Iterable[ta.Tuple[str, str]]:
    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        if '=' in line:
            k, _, v = line.partition('=')
        else:
            k, v = line, ''
        k = k.strip()
        v = v.strip().strip("'").strip('"')
        yield k, v


class Parser:

    def __init__(self, buf: str) -> None:
        super().__init__()

        self._buf = check.isinstance(buf, str)
        self._pos = 0

    def read_pattern(self, pat: ta.Pattern) -> ta.Match:
        match = check.not_none(pat.match(self._buf, self._pos))
        check.state(match.end() >= self._pos)
        self._pos = match.end()
        return match


def parse(buf: str) -> ta.Iterable[ta.Tuple[str, ta.Optional[str]]]:
    raise NotImplementedError
