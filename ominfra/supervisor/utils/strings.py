# ruff: noqa: UP006 UP007 UP045
import typing as ta


##


def as_bytes(s: ta.Union[str, bytes], encoding: str = 'utf8') -> bytes:
    if isinstance(s, bytes):
        return s
    else:
        return s.encode(encoding)


@ta.overload
def find_prefix_at_end(haystack: str, needle: str) -> int:
    ...


@ta.overload
def find_prefix_at_end(haystack: bytes, needle: bytes) -> int:
    ...


def find_prefix_at_end(haystack, needle):
    l = len(needle) - 1
    while l and not haystack.endswith(needle[:l]):
        l -= 1
    return l


##


ANSI_ESCAPE_BEGIN = b'\x1b['
ANSI_TERMINATORS = (b'H', b'f', b'A', b'B', b'C', b'D', b'R', b's', b'u', b'J', b'K', b'h', b'l', b'p', b'm')


def strip_escapes(s: bytes) -> bytes:
    """Remove all ANSI color escapes from the given string."""

    result = b''
    show = 1
    i = 0
    l = len(s)
    while i < l:
        if show == 0 and s[i:i + 1] in ANSI_TERMINATORS:
            show = 1
        elif show:
            n = s.find(ANSI_ESCAPE_BEGIN, i)
            if n == -1:
                return result + s[i:]
            else:
                result = result + s[i:n]
                i = n
                show = 0
        i += 1
    return result


##


class SuffixMultiplier:
    # d is a dictionary of suffixes to integer multipliers. If no suffixes match, default is the multiplier. Matches are
    # case insensitive. Return values are in the fundamental unit.
    def __init__(self, d, default=1):
        super().__init__()

        self._d = d
        self._default = default
        # all keys must be the same size
        self._keysz = None
        for k in d:
            if self._keysz is None:
                self._keysz = len(k)
            elif self._keysz != len(k):
                raise ValueError(k)

    def __call__(self, v: ta.Union[str, int]) -> int:
        if isinstance(v, int):
            return v
        v = v.lower()
        for s, m in self._d.items():
            if v[-self._keysz:] == s:  # type: ignore
                return int(v[:-self._keysz]) * m  # type: ignore
        return int(v) * self._default


parse_bytes_size = SuffixMultiplier({
    'kb': 1024,
    'mb': 1024 * 1024,
    'gb': 1024 * 1024 * 1024,
})


#


def parse_octal(arg: ta.Union[str, int]) -> int:
    if isinstance(arg, int):
        return arg
    try:
        return int(arg, 8)
    except (TypeError, ValueError):
        raise ValueError(f'{arg} can not be converted to an octal type')  # noqa
