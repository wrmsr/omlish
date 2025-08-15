"""
TODO:
 - use importlib.util.resolve_name
"""
import importlib.util
import sys
import types
import typing as ta


##


def can_import(name: str, package: str | None = None) -> bool:
    try:
        spec = importlib.util.find_spec(name, package)
    except ImportError:
        return False
    else:
        return spec is not None


##


def try_import(spec: str) -> types.ModuleType | None:
    s = spec.lstrip('.')
    l = len(spec) - len(s)
    try:
        return __import__(s, globals(), level=l)
    except ImportError:
        return None


##


def resolve_import_name(name: str, package: str | None = None) -> str:
    # FIXME: importlib.util.resolve_name
    level = 0

    if name.startswith('.'):
        if not package:
            raise TypeError("the 'package' argument is required to perform a relative import for {name!r}")
        for character in name:
            if character != '.':
                break
            level += 1

    name = name[level:]

    if not isinstance(name, str):
        raise TypeError(f'module name must be str, not {type(name)}')
    if level < 0:
        raise ValueError('level must be >= 0')
    if level > 0:
        if not isinstance(package, str):
            raise TypeError('__package__ not set to a string')
        elif not package:
            raise ImportError('attempted relative import with no known parent package')
    if not name and level == 0:
        raise ValueError('Empty module name')

    if level > 0:
        bits = package.rsplit('.', level - 1)  # type: ignore
        if len(bits) < level:
            raise ImportError('attempted relative import beyond top-level package')
        base = bits[0]
        name = f'{base}.{name}' if name else base

    return name


##


def get_real_module_name(globals: ta.Mapping[str, ta.Any]) -> str:  # noqa
    module = sys.modules[globals['__name__']]

    if module.__spec__ and module.__spec__.name:
        return module.__spec__.name

    if module.__package__:
        return module.__package__

    raise RuntimeError("Can't determine real module name")
