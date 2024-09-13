"""
TODO:
 - whitelist packages
"""
import importlib.abc
import importlib.machinery
import importlib.util
import os.path
import sys
import types
import typing as ta

from omlish import check

from . import build


##


def load_dynamic(name: str, path: str) -> types.ModuleType:
    import importlib.machinery
    loader = importlib.machinery.ExtensionFileLoader(name, path)

    # Issue #24748: Skip the sys.modules check in _load_module_shim; always load new extension
    spec = importlib.machinery.ModuleSpec(name=name, loader=loader, origin=path)

    import importlib._bootstrap  # FIXME:  # noqa
    return importlib._bootstrap._load(spec)  # noqa


##


class CextImportLoader(importlib.machinery.ExtensionFileLoader):

    def __init__(
            self,
            filename: str,
    ) -> None:
        module_name = os.path.splitext(os.path.basename(filename))[0]
        super().__init__(module_name, filename)

    def create_module(self, spec: importlib.machinery.ModuleSpec) -> types.ModuleType:
        so_path = build.build_ext(build.BuildExt(spec.name, check.non_empty_str(spec.origin)))
        self.path = so_path  # noqa
        spec.origin = so_path
        return super().create_module(spec)

    def exec_module(self, module):
        return super().exec_module(module)


CEXT_EXTENSIONS = ['.c', '.cc', '.cpp', '.cxx']


class CextImportMetaFinder(importlib.abc.MetaPathFinder):

    def __init__(
            self,
            extensions: ta.AbstractSet[str] = frozenset(CEXT_EXTENSIONS),
    ) -> None:
        super().__init__()
        self._extensions = extensions

    def find_spec(
            self,
            fullname: str,
            path: ta.Sequence[str] | None,
            target: types.ModuleType | None = None,
    ) -> importlib.machinery.ModuleSpec | None:
        if not path:
            path = [os.getcwd(), *sys.path]  # top level import --
        if '.' in fullname:
            *parents, name = fullname.split('.')
        else:
            name = fullname

        for entry in path:
            for ext in self._extensions:
                if os.path.isdir(os.path.join(entry, name)):
                    # this module has child modules
                    filename = os.path.join(entry, name, '__init__' + ext)
                    submodule_locations = [os.path.join(entry, name)]
                else:
                    filename = os.path.join(entry, name + ext)
                    submodule_locations = None
                if not os.path.exists(filename):
                    continue

                return importlib.util.spec_from_file_location(
                    fullname,
                    filename,
                    loader=CextImportLoader(filename),
                    submodule_search_locations=submodule_locations,
                )

        return None  # we don't know how to import this


#


def _get_installed_importers() -> list[CextImportMetaFinder]:
    return [i for i in sys.meta_path if isinstance(i, CextImportMetaFinder)]


def is_installed() -> bool:
    return bool(_get_installed_importers())


def install(*, flush: bool = True) -> bool:
    if _get_installed_importers():
        return False

    sys.meta_path.append(CextImportMetaFinder())

    if flush:
        importlib.invalidate_caches()

    return True


def uninstall(*, flush: bool = False) -> bool:
    ret = False

    for i in _get_installed_importers():
        sys.meta_path.remove(i)
        ret = True

    if ret and flush:
        importlib.invalidate_caches()

    return ret
