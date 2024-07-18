"""
TODO:
 - remove imp
 - whitelist packages
"""
import dataclasses as dc
import importlib
import importlib.abc
import importlib.machinery
import os.path
import sys
import types
import typing as ta

from . import build


def load_dynamic(name: str, path: str) -> types.ModuleType:
    import importlib.machinery
    loader = importlib.machinery.ExtensionFileLoader(name, path)

    # Issue #24748: Skip the sys.modules check in _load_module_shim; always load new extension
    spec = importlib.machinery.ModuleSpec(name=name, loader=loader, origin=path)

    import importlib._bootstrap  # FIXME:  # noqa
    return importlib._bootstrap._load(spec)  # noqa


class CExtensionLoader(importlib.abc.Loader):

    def __init__(self, fullname: str, path: str) -> None:
        super().__init__()

        self._fullname = fullname
        self._path = path

    def load_module(self, fullname: str) -> types.ModuleType:
        so_path = build.build_ext(fullname, self._path)
        return load_dynamic(self._fullname, so_path)


LoaderDetails: ta.TypeAlias = tuple[type[importlib.abc.Loader], list[str]]
loader_details = (CExtensionLoader, ['.c', '.cc', '.cpp', '.cxx'])


##


@dc.dataclass(frozen=True)
class FileFinderPathHook:
    lds: ta.Sequence[LoaderDetails]

    def __call__(self, path: str) -> importlib.machinery.FileFinder:
        if not path:
            path = os.getcwd()
        if not os.path.isdir(path):
            raise ImportError('only directories are supported', path=path)
        return importlib.machinery.FileFinder(path, *self.lds)


def _is_c_loader(h: ta.Any) -> bool:
    return (
        isinstance(h, FileFinderPathHook) and
        h.lds == [loader_details]
    )


def is_installed() -> bool:
    return any(h for h in sys.path_hooks if _is_c_loader(h))


def _install(*, flush: bool = False) -> None:
    sys.path_hooks.insert(0, FileFinderPathHook([loader_details]))
    sys.path_importer_cache.clear()
    if flush:
        importlib.invalidate_caches()


def install(*, flush: bool = False) -> None:
    if not is_installed():
        _install(flush=flush)


def uninstall(*, flush: bool = False) -> None:
    sys.path_hooks = [h for h in sys.path_hooks if not _is_c_loader(h)]
    sys.path_importer_cache.clear()
    if flush:
        importlib.invalidate_caches()
