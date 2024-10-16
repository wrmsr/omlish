import contextlib
import functools
import importlib.util
import sys
import types
import typing as ta

from .cached import cached_function


##


def can_import(name: str, package: str | None = None) -> bool:
    try:
        spec = importlib.util.find_spec(name, package)
    except ImportError:
        return False
    else:
        return spec is not None


##


def lazy_import(name: str, package: str | None = None) -> ta.Callable[[], ta.Any]:
    return cached_function(functools.partial(importlib.import_module, name, package=package))


def proxy_import(
        name: str,
        package: str | None = None,
        extras: ta.Iterable[str] | None = None,
) -> types.ModuleType:
    if isinstance(extras, str):
        raise TypeError(extras)

    omod = None

    def __getattr__(att):  # noqa
        nonlocal omod
        if omod is None:
            omod = importlib.import_module(name, package=package)
            if extras:
                for x in extras:
                    importlib.import_module(f'{name}.{x}', package=package)
        return getattr(omod, att)

    lmod = types.ModuleType(name)
    lmod.__getattr__ = __getattr__  # type: ignore
    return lmod


##


def import_module(dotted_path: str) -> types.ModuleType:
    if not dotted_path:
        raise ImportError(dotted_path)
    mod = __import__(dotted_path, globals(), locals(), [])
    for name in dotted_path.split('.')[1:]:
        try:
            mod = getattr(mod, name)
        except AttributeError:
            raise AttributeError(f'Module {mod!r} has no attribute {name!r}') from None
    return mod


def import_module_attr(dotted_path: str) -> ta.Any:
    module_name, _, class_name = dotted_path.rpartition('.')
    mod = import_module(module_name)
    try:
        return getattr(mod, class_name)
    except AttributeError:
        raise AttributeError(f'Module {module_name!r} has no attr {class_name!r}') from None


SPECIAL_IMPORTABLE: ta.AbstractSet[str] = frozenset([
    '__init__.py',
    '__main__.py',
])


def yield_importable(
        package_root: str,
        *,
        recursive: bool = False,
        filter: ta.Callable[[str], bool] | None = None,  # noqa
        include_special: bool = False,
) -> ta.Iterator[str]:
    from importlib import resources

    def rec(cur):
        if cur.split('.')[-1] == '__pycache__':
            return

        try:
            module = sys.modules[cur]
        except KeyError:
            try:
                __import__(cur)
            except ImportError:
                return
            module = sys.modules[cur]

        # FIXME: pyox
        if getattr(module, '__file__', None) is None:
            return

        for file in resources.files(cur).iterdir():
            if file.is_file() and file.name.endswith('.py'):
                if not (include_special or file.name not in SPECIAL_IMPORTABLE):
                    continue

                name = cur + '.' + file.name[:-3]
                if filter is not None and not filter(name):
                    continue

                yield name

            elif recursive and file.is_dir():
                name = cur + '.' + file.name
                if filter is not None and not filter(name):
                    continue
                with contextlib.suppress(ImportError, NotImplementedError):
                    yield from rec(name)

    yield from rec(package_root)


def yield_import_all(
        package_root: str,
        *,
        globals: dict[str, ta.Any] | None = None,  # noqa
        locals: dict[str, ta.Any] | None = None,  # noqa
        recursive: bool = False,
        filter: ta.Callable[[str], bool] | None = None,  # noqa
        include_special: bool = False,
) -> ta.Iterator[str]:
    for import_path in yield_importable(
            package_root,
            recursive=recursive,
            filter=filter,
            include_special=include_special,
    ):
        __import__(import_path, globals=globals, locals=locals)
        yield import_path


def import_all(
        package_root: str,
        *,
        recursive: bool = False,
        filter: ta.Callable[[str], bool] | None = None,  # noqa
        include_special: bool = False,
) -> None:
    for _ in yield_import_all(
            package_root,
            recursive=recursive,
            filter=filter,
            include_special=include_special,
    ):
        pass


def try_import(spec: str) -> types.ModuleType | None:
    s = spec.lstrip('.')
    l = len(spec) - len(s)
    try:
        return __import__(s, globals(), level=l)
    except ImportError:
        return None


##


def resolve_import_name(name: str, package: str | None = None) -> str:
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


_REGISTERED_CONDITIONAL_IMPORTS: dict[str, list[str] | None] = {}


def _register_conditional_import(when: str, then: str, package: str | None = None) -> None:
    wn = resolve_import_name(when, package)
    tn = resolve_import_name(then, package)
    if tn in sys.modules:
        return
    if wn in sys.modules:
        __import__(tn)
    else:
        tns = _REGISTERED_CONDITIONAL_IMPORTS.setdefault(wn, [])
        if tns is None:
            raise Exception(f'Conditional import trigger already cleared: {wn=} {tn=}')
        tns.append(tn)


def _trigger_conditional_imports(package: str) -> None:
    tns = _REGISTERED_CONDITIONAL_IMPORTS.get(package, [])
    if tns is None:
        raise Exception(f'Conditional import trigger already cleared: {package=}')
    _REGISTERED_CONDITIONAL_IMPORTS[package] = None
    for tn in tns:
        __import__(tn)
