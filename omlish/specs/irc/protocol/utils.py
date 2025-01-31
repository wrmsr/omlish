import itertools
import operator


def truncate_utf8_safe(string: str, length: int) -> str:
    return string[:length] \
        .encode('utf-8', 'ignore') \
        .decode('utf-8', 'ignore')


def find_utf8_truncation_point(buf: bytes | bytearray, length: int) -> int:
    if len(buf) < length:
        raise ValueError(buf)
    cs = itertools.accumulate(
        (len(c.encode('utf-8')) for c in buf.decode('utf-8')),
        operator.add,
        initial=0,
    )
    return next(i for i, o in enumerate(cs) if o >= length)


def trim_initial_spaces(string: str) -> str:
    return string.lstrip(' ')


def is_ascii(string: str) -> bool:
    return all(ord(c) < 128 for c in string)
