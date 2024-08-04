import sys
from importlib.metadata import EntryPoint as _EntryPoint


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
    import _io
    return isinstance(stream, _io._TextIOBase)


def import_spec(spec):
    return _EntryPoint(None, spec, None).load()


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


def find_prefix_at_end(haystack, needle):
    l = len(needle) - 1
    while l and not haystack.endswith(needle[:l]):
        l -= 1
    return l


class ExitNow(Exception):
    pass
