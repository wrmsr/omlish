import importlib.resources as _importlib_resources
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


def resource_filename(package, path):
    return str(_importlib_resources.files(package).joinpath(path))
