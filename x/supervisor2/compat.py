import importlib.metadata
import io
import sys
import typing as ta


def as_bytes(s, encoding='utf8'):
    if isinstance(s, bytes):
        return s
    else:
        return s.encode(encoding)


def as_string(s, encoding='utf8'):
    if isinstance(s, str):
        return s
    else:
        return s.decode(encoding)


def is_text_stream(stream):
    return isinstance(stream, io.TextIOBase)


def import_spec(spec):
    return importlib.metadata.EntryPoint(None, spec, None).load()  # noqa


def compact_traceback():
    t, v, tb = sys.exc_info()
    tbinfo = []
    assert tb  # Must have a traceback
    while tb:
        tbinfo.append((
            tb.tb_frame.f_code.co_filename,
            tb.tb_frame.f_code.co_name,
            str(tb.tb_lineno),
        ))
        tb = tb.tb_next

    # just to be safe
    del tb

    file, function, line = tbinfo[-1]
    info = ' '.join(['[%s|%s|%s]' % x for x in tbinfo])
    return (file, function, line), t, v, info


def find_prefix_at_end(haystack: str, needle: str) -> int:
    l = len(needle) - 1
    while l and not haystack.endswith(needle[:l]):
        l -= 1
    return l


class ExitNow(Exception):
    pass


def expand(s: str, expansions: ta.Any, name: str) -> str:
    try:
        return s % expansions
    except KeyError as ex:
        available = list(expansions.keys())
        available.sort()
        raise ValueError(
            'Format string %r for %r contains names (%s) which cannot be '
            'expanded. Available names: %s' % (s, name, str(ex), ', '.join(available)))
    except Exception as ex:
        raise ValueError('Format string %r for %r is badly formatted: %s' % (s, name, str(ex)))
