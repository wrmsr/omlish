import contextlib
import functools
import importlib.util
import sys
import types
import typing as ta

from .cached import cached_function


##


def can_import(name: str, package: str | None = None) -> bool:
    return importlib.util.find_spec(name, package) is not None


##


def lazy_import(name: str, package: str | None = None) -> ta.Callable[[], ta.Any]:
    return cached_function(functools.partial(importlib.import_module, name, package=package))


def proxy_import(name: str, package: str | None = None) -> types.ModuleType:
    omod = None

    def __getattr__(att):  # noqa
        nonlocal omod
        if omod is None:
            omod = importlib.import_module(name, package=package)
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
