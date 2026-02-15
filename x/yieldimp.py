import dataclasses as dc
import importlib.abc
import importlib.machinery
import importlib.util
import inspect
import os.path
import pathlib
import sys
import types
import typing as ta

from omlish.lang.imports.proxy import proxy_import


if ta.TYPE_CHECKING:
    import importlib.resources as importlib_resources
else:
    importlib_resources = proxy_import('importlib.resources')


ModuleSpec: ta.TypeAlias = importlib.machinery.ModuleSpec

ImportableKind: ta.TypeAlias = ta.Literal['module', 'package']


##


class MetaPathFinderProtocol(ta.Protocol):
    def find_spec(
            self,
            fullname: str,
            path: ta.Sequence[str] | None,
            target: types.ModuleType | None = None,
    ) -> importlib.machinery.ModuleSpec | None: ...

    def invalidate_caches(self) -> None: ...


@dc.dataclass(frozen=True)
class MetaPathSpec:
    finder: MetaPathFinderProtocol
    spec: ModuleSpec


def find_meta_path_spec(
        fullname: str,
        path: ta.Sequence[str] | None = None,
        target: types.ModuleType | None = None,
) -> MetaPathSpec | None:
    # FIXME WHAT THE FUCK:
    # https://github.com/python/cpython/blob/26b7df2430cd5a9ee772bfa6ee03a73bd0b11619/Lib/importlib/_bootstrap_external.py#L1385
    # x.asynclite.anyio IMPORTS ANYIO BECAUSE TAIL_MODULE = ANYIO WHAT THE FUCKING FUCK
    for finder in sys.meta_path:
        # https://github.com/python/cpython/blob/6aeb0d5b2ae45beb8456a96faef416575fb25058/Lib/importlib/_bootstrap.py#L1257-L1260
        try:
            find_spec = finder.find_spec
        except AttributeError:
            continue
        if (spec := find_spec(fullname, path, target)) is not None:
            return MetaPathSpec(ta.cast(MetaPathFinderProtocol, finder), spec)
    return None


##


def find_module_or_spec(fullname: str) -> types.ModuleType | MetaPathSpec | None:
    if fullname in sys.modules:
        if (module := sys.modules[fullname]) is None:
            return None
        try:
            spec = module.__spec__
        except AttributeError:
            raise ValueError(f'{fullname}.__spec__ is not set') from None
        if spec is None:
            raise ValueError(f'{fullname}.__spec__ is None')
        return module

    if (mp_spec := find_meta_path_spec(fullname)) is not None:
        return mp_spec

    return None


def find_ancestor_module_or_spec(fullname: str) -> types.ModuleType | MetaPathSpec | None:
    if (spec := find_module_or_spec(fullname)) is not None:
        return spec

    p = len(fullname)
    while (p := fullname.rfind('.', 0, p)) >= 0:
        if (ancestor := find_module_or_spec(fullname[:p])) is not None:
            return ancestor

    return None


##


def is_simple_fs_module_spec(spec: ModuleSpec) -> bool:
    return (
            isinstance(spec.loader, importlib.machinery.SourceFileLoader) and
            spec.origin is not None and
            len(spec.submodule_search_locations or []) == 1 and
            os.path.basename(spec.origin) == '__init__.py' and
            os.path.isfile(spec.origin)
    )


def get_simple_fs_package_path(package_name: str) -> str | None:
    # Note: WE *CANNOT* CALL `importlib.util.find_spec` UNDER ANY CIRCUMSTANCES as that unconditionally imports at least
    # the parent package, and the entire point of 'simple_fs' is to avoid that.

    if (found := find_ancestor_module_or_spec(package_name)) is None:
        return None

    spec: ModuleSpec
    if isinstance(found, types.ModuleType):
        spec = found.__spec__
    elif isinstance(found, MetaPathSpec):
        spec = found.spec
    else:
        raise TypeError(found)

    if not is_simple_fs_module_spec(spec):
        return None

    sd = os.path.dirname(spec.origin)
    if spec.name == package_name:
        return sd

    pn_ps = package_name.split('.')
    sn_ps = spec.name.split('.')
    if not (len(pn_ps) > len(sn_ps) and pn_ps[:len(sn_ps)] == sn_ps):
        return None

    return os.path.join(sd, *pn_ps[len(sn_ps):])


##


SPECIAL_MODULE_NAMES: ta.AbstractSet[str] = frozenset([
    '__init__',
    '__main__',
])


IGNORED_DIR_NAMES: ta.AbstractSet[str] = frozenset([
    '__pycache__',
])


##


@dc.dataclass(frozen=True, kw_only=True)
class Importable:
    name: str
    kind: ImportableKind
    fs_path: str | None = None


@dc.dataclass()
class YieldImportableNotSimpleFsError(Exception):
    package_root: str


@dc.dataclass(frozen=True, kw_only=True)
class ImportableYielder:
    raise_on_exception: bool = False

    #

    def _gen_from_fs(self, pkg_name: str, dir_path: str) -> ta.Iterator[Importable]:
        for name in sorted(os.listdir(dir_path)):
            path = os.path.join(dir_path, name)

            if (
                    os.path.isfile(path) and
                    (mod_name := inspect.getmodulename(path)) is not None
            ):
                yield Importable(
                    name='.'.join([pkg_name, mod_name]),
                    kind='module',
                    fs_path=path,
                )

            elif (
                    os.path.isdir(path) and
                    name not in IGNORED_DIR_NAMES and
                    any(
                        # https://github.com/python/cpython/blob/fffd38b2dd9706f4a1e3ee842441abffdf9a57b9/Lib/pkgutil.py#L158-L162
                        inspect.getmodulename(child_path) == '__init__'
                        for child_name in os.listdir(path)
                        if os.path.isfile(child_path := os.path.join(path, child_name))
                    )
            ):
                yield Importable(
                    name='.'.join([pkg_name, name]),
                    kind='package',
                    fs_path=path,
                )

    def _try_import(self, pkg_name: str, *, raise_: bool = False) -> types.ModuleType | None:
        try:
            return sys.modules[pkg_name]
        except KeyError:
            pass

        try:
            return importlib.import_module(pkg_name)
        except Exception:  # noqa
            if raise_:
                raise

        return None

    def _gen_from_resources(self, pkg_name: str) -> ta.Iterator[Importable]:
        # importlib.resources actually imports the package, so import it ourselves to suppress the exception.
        # https://github.com/python/cpython/blob/fffd38b2dd9706f4a1e3ee842441abffdf9a57b9/Lib/importlib/resources/_common.py#L82
        if (module := self._try_import(pkg_name, raise_=self.raise_on_exception)) is None:  # noqa
            return

        for item in sorted(importlib_resources.files(pkg_name).iterdir(), key=lambda i: i.name):  # noqa
            if (
                    item.is_file() and
                    (mod_name := inspect.getmodulename(item.name)) is not None
            ):
                yield Importable(
                    name='.'.join([pkg_name, mod_name]),
                    kind='module',
                    fs_path=str(item) if isinstance(item, pathlib.Path) else None,
                )

            elif (
                    item.is_dir() and
                    item.name not in IGNORED_DIR_NAMES and
                    self._try_import(item_pkg_name := '.'.join([pkg_name, item.name])) is not None
            ):
                yield Importable(
                    name=item_pkg_name,
                    kind='package',
                    fs_path=str(item) if isinstance(item, pathlib.Path) else None,
                )

    simple_fs: bool | ta.Literal['only_silent', 'only_raise'] = True

    def _gen_one(self, pkg_name: str) -> ta.Iterator[Importable]:
        if self.simple_fs and (dir_path := get_simple_fs_package_path(pkg_name)) is not None:
            return self._gen_from_fs(pkg_name, dir_path)

        if self.simple_fs == 'only_silent':
            return iter([])
        if self.simple_fs == 'only_raise':
            raise YieldImportableNotSimpleFsError(pkg_name)

        return self._gen_from_resources(pkg_name)

    #

    kinds: ta.AbstractSet[ImportableKind] | None = None  # noqa
    filter: ta.Callable[[Importable], bool] | None = None  # noqa

    def _filter_inner(self, item: Importable) -> bool:
        if not self.include_special and item.name.split('.')[-1] in SPECIAL_MODULE_NAMES:
            return False

        if self.filter is not None and not self.filter(item):
            return False

        return True

    #

    include_special: bool = False

    def _filter_outer(self, item: Importable) -> bool:
        if self.kinds is not None and item.kind not in self.kinds:
            return False

        return True

    #

    recursive: bool = False

    def __call__(self, pkg_name: str) -> ta.Iterator[Importable]:
        for item in self._gen_one(pkg_name):
            if not self._filter_inner(item):
                continue

            if self._filter_outer(item):
                yield item

            if item.kind == 'package' and self.recursive:
                yield from self(item.name)


##


def _main() -> None:
    mods_before = set(sys.modules)

    for item in ImportableYielder(
        # simple_fs=False,
        recursive=True,
    )('x'):
        print(item)

    mods_after = set(sys.modules)
    print('\n'.join(sorted(mods_after - mods_before)))


if __name__ == '__main__':
    _main()
