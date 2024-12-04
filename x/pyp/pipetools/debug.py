from itertools import chain


def set_name(name, f):
    try:
        f.__pipetools__name__ = name
    except (AttributeError, UnicodeEncodeError):
        pass
    return f


def get_name(f):
    from .main import Pipe
    pipetools_name = getattr(f, '__pipetools__name__', None)
    if pipetools_name:
        return pipetools_name() if callable(pipetools_name) else pipetools_name

    if isinstance(f, Pipe):
        return repr(f)

    return f.__name__ if hasattr(f, '__name__') else repr(f)


def repr_args(*args, **kwargs):
    return ', '.join(chain(
        map('{0!r}'.format, args),
        map('{0[0]}={0[1]!r}'.format, kwargs.items())))
