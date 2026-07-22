"""
TODO:
 - overhaul this - use pkgutil.walk_packages unless caller needs non-importing (which this currently doesn't do anyway),
   and support namespace packages if they do.
"""
import contextlib
import sys
import typing as ta


##


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
        raise_on_failure: bool = False,
) -> ta.Iterator[str]:
    import importlib.resources

    def rec(cur):
        if cur.split('.')[-1] == '__pycache__':
            return

        try:
            module = sys.modules[cur]
        except KeyError:
            module = importlib.import_module(cur)

        # FIXME: pyox
        if getattr(module, '__file__', None) is None:
            return

        for file in importlib.resources.files(cur).iterdir():
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

                if raise_on_failure:
                    yield from rec(name)

                else:
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
        raise_on_failure: bool = False,
) -> ta.Iterator[str]:
    for import_path in yield_importable(
            package_root,
            recursive=recursive,
            filter=filter,
            include_special=include_special,
            raise_on_failure=raise_on_failure,
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
