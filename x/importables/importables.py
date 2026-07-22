"""
Yields importable specs without importing anything.

The core problem with the importlib-based approach (see `traversal.py` / `ImportlibImportableYielder`) is that both
`importlib.resources.files` and `importlib.util.find_spec` unconditionally import (at minimum) the parent package of
whatever they're asked about - meaning arbitrary `__init__.py` code runs. `ZeroImportImportableYielder` avoids this by
speaking the import machinery's *finder* protocols directly, which are pure lookups (stat calls / zip directory reads)
and never execute module code:

 - Top-level names are resolved by walking `sys.meta_path` finders' `find_spec` - for the stdlib finders
   (`BuiltinImporter`, `FrozenImporter`) this is a pure lookup, and well-behaved third-party meta path finders don't
   import in `find_spec` either.

 - `importlib.machinery.PathFinder` is *not* called directly for anything below the top level:

    - Its `find_spec` must be given the parent package's `__path__` - the path-entry finders it delegates to
      (`FileFinder`, `zipimporter`) match only on the *tail* of the dotted name, so calling it with a dotted name and
      the wrong path (e.g. `sys.path`) happily returns garbage specs for unrelated packages that happen to share the
      tail name (see the note in `new.py`).

    - When it does find a namespace package it wraps the portions in a `_NamespacePath`, whose `__init__` reaches into
      `sys.modules[parent].__path__` - raising `KeyError` when the parent is (deliberately!) not imported.

   Instead, its documented algorithm is replayed here over the parent's search locations using the public path-entry
   finder protocol (`sys.path_hooks` -> `finder.find_spec(name)`), aggregating namespace portions manually. This
   handles filesystem directories and zip/pyz archives (via the stdlib `zipimporter` hook) identically, all without
   importing.

 - Child *candidates* are enumerated per path entry - `os.scandir` for directories, direct `zipfile` directory reads
   for zip/pyz archives (including archive-internal pseudo-paths like `/x/app.pyz/pkg`), and an `iter_modules`
   protocol fallback for exotic path entry types. Candidates are just names; the finder protocol above is the single
   source of truth for what each name actually resolves to.

 - `sys.modules` is authoritative for *named* lookups: already-imported packages contribute their live (possibly
   runtime-mutated, e.g. `pkgutil.extend_path`) `__path__`, but only after an identity check (`__file__` vs the
   resolved spec's origin) so that enumerating an unrelated tree (e.g. an un-imported pyz via `yield_path_entry`)
   never confuses a name collision with the live module.

Deliberate limitations (the well-behaved ~99% is the target, not the pathological 1%):

 - Meta path finders are only consulted for root resolution - packages whose *submodules* are conjured by meta path
   hooks (rather than found on the parent's `__path__`) won't be seen.
 - By default only identifier-named modules/packages are yielded - `foo-bar.py` isn't reachable by any dotted import
   statement, though `importlib.import_module` / `__import__` can in fact import it (see e.g. pip's `__pip-runner__`);
   set `identifiers_only=False` to include such names. Dotted stems (`foo.bar.py`) are always excluded - the resulting
   name would collide with real nesting and resolve to garbage.
 - Directory symlink cycles are not guarded against (same as `traversal.py`).
 - Instances cache zip directories and path-entry finders; use a fresh instance (or `invalidate_caches`) if sys.path
   contents change materially mid-flight.
 - "Imports nothing" means no *discovered* code is ever executed - the stdlib may still lazily self-load internals the
   first time machinery is exercised (e.g. `zipfile` pulls in `encodings.cp437` on first read of a zip directory).
"""
import abc
import dataclasses as dc
import importlib.machinery
import inspect
import os.path
import sys
import types
import typing as ta
import zipfile


##


ModuleSpec: ta.TypeAlias = importlib.machinery.ModuleSpec

ImportableKind: ta.TypeAlias = ta.Literal[
    'module',
    'package',
    'namespace_package',
]


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
    origin: str | None = None
    search_locations: tuple[str, ...] | None = None

    @property
    def is_special(self) -> bool:
        return self.name.rpartition('.')[2] in SPECIAL_MODULE_NAMES


@dc.dataclass(frozen=True, kw_only=True)
class YieldImportableOptions:
    recursive: bool = False

    filter: ta.Callable[[Importable], bool] | None = None  # noqa

    # Yield `__init__` / `__main__` as importables of their own (they are - importing `pkg.__init__` re-executes it).
    include_special: bool = False

    # PEP 420 namespace packages (and their contents). Off by default to match `traversal.py`, which pruned them (any
    # random data subdirectory of a package is technically an importable namespace portion).
    include_namespace_packages: bool = False

    # Restricts what is *yielded*, not what is recursed into - `kinds=frozenset(['module'])` with `recursive=True`
    # still descends packages.
    kinds: ta.AbstractSet[ImportableKind] | None = None  # noqa

    # When False, non-identifier (but still undotted) names like 'foo-bar' are included - unreachable by any `import`
    # statement, but importable via `importlib.import_module` / `__import__`.
    identifiers_only: bool = True

    raise_on_failure: bool = False


DEFAULT_YIELD_IMPORTABLE_OPTIONS = YieldImportableOptions()


##


class ImportableYielder(abc.ABC):
    def __init__(self, options: YieldImportableOptions = DEFAULT_YIELD_IMPORTABLE_OPTIONS) -> None:
        super().__init__()

        self._options = options

    @property
    def options(self) -> YieldImportableOptions:
        return self._options

    #

    @abc.abstractmethod
    def _resolve_root(self, name: str) -> Importable:
        """
        Resolves the root package itself (which is not yielded). Always raises on failure - an unresolvable root is a
        caller error, not a traversal failure.
        """

        raise NotImplementedError

    @abc.abstractmethod
    def _yield_children(self, pkg: Importable) -> ta.Iterator[Importable]:
        raise NotImplementedError

    #

    def yield_importable(self, package_root: str) -> ta.Iterator[Importable]:
        root = self._resolve_root(package_root)
        yield from self._walk(root)

    def _walk(self, pkg: Importable) -> ta.Iterator[Importable]:
        opts = self._options

        try:
            children = sorted(self._yield_children(pkg), key=lambda i: i.name)
        except Exception:  # noqa
            if opts.raise_on_failure:
                raise
            return

        for child in children:
            if child.is_special and not opts.include_special:
                continue

            if child.kind == 'namespace_package' and not opts.include_namespace_packages:
                continue

            if opts.filter is not None and not opts.filter(child):
                continue

            if opts.kinds is None or child.kind in opts.kinds:
                yield child

            if opts.recursive and child.kind in ('package', 'namespace_package'):
                yield from self._walk(child)

    #

    def _candidate_name_ok(self, name: str) -> bool:
        if not name or '.' in name:
            return False
        if self._options.identifiers_only and not name.isidentifier():
            return False
        return True

    #

    @staticmethod
    def _module_importable(name: str, mod: types.ModuleType) -> Importable:
        mod_path = getattr(mod, '__path__', None)
        mod_file = getattr(mod, '__file__', None)

        kind: ImportableKind
        if mod_path is not None:
            kind = 'package' if mod_file is not None else 'namespace_package'
        else:
            kind = 'module'

        return Importable(
            name=name,
            kind=kind,
            origin=mod_file,
            search_locations=tuple(mod_path) if mod_path is not None else None,
        )

    @staticmethod
    def _spec_importable(spec: ModuleSpec) -> Importable:
        kind: ImportableKind
        if spec.submodule_search_locations is not None:
            kind = 'package' if spec.origin is not None else 'namespace_package'
        else:
            kind = 'module'

        return Importable(
            name=spec.name,
            kind=kind,
            origin=spec.origin,
            search_locations=(
                tuple(spec.submodule_search_locations)
                if spec.submodule_search_locations is not None
                else None
            ),
        )


##


class ZeroImportImportableYielder(ImportableYielder):
    def __init__(self, options: YieldImportableOptions = DEFAULT_YIELD_IMPORTABLE_OPTIONS) -> None:
        super().__init__(options)

        self._path_entry_finder_cache: dict[str, ta.Any] = {}
        self._zip_namelist_cache: dict[str, list[str]] = {}

    def invalidate_caches(self) -> None:
        self._path_entry_finder_cache.clear()
        self._zip_namelist_cache.clear()

    #

    def yield_path_entry(self, path_entry: str) -> ta.Iterator[Importable]:
        """
        Yields the importables reachable from a single path entry - a directory, or a zip/pyz archive (or a directory
        within one) - which need not be on sys.path and is never imported. Names are relative to the entry ('pkg',
        'pkg.sub', ...).
        """

        yield from self._walk(Importable(
            name='',
            kind='namespace_package',
            search_locations=(path_entry,),
        ))

    #

    def _resolve_root(self, name: str) -> Importable:
        if not name or any(not p for p in name.split('.')):
            raise ValueError(f'Invalid module name: {name!r}')

        parts = name.split('.')
        search: tuple[str, ...] | None = None
        imp: Importable | None = None

        for i in range(len(parts)):
            cur = '.'.join(parts[:i + 1])

            # sys.modules is authoritative for named lookups - an already-imported package's live (possibly mutated)
            # __path__ is *more* correct than anything re-derivable from its spec.
            if cur in sys.modules:
                if (mod := sys.modules[cur]) is None:
                    raise ModuleNotFoundError(f'No module named {cur!r}', name=cur)
                imp = self._module_importable(cur, mod)
            else:
                if (spec := self._find_spec(cur, search)) is None:
                    raise ModuleNotFoundError(f'No module named {cur!r}', name=cur)
                imp = self._spec_importable(spec)

            search = imp.search_locations
            if search is None and i < len(parts) - 1:
                raise ModuleNotFoundError(f'{cur!r} is not a package', name=cur)

        return ta.cast(Importable, imp)

    def _find_spec(self, fullname: str, path: ta.Sequence[str] | None) -> ModuleSpec | None:
        for finder in sys.meta_path:
            if finder is importlib.machinery.PathFinder:
                # PathFinder is unsafe here on two counts (garbage tail-name matches against the wrong path, and
                # _NamespacePath's KeyError on unimported parents - see module docstring), so its algorithm is replayed
                # via the path-entry finder protocol instead.
                spec = self._find_path_spec(fullname, path if path is not None else sys.path)
            else:
                try:
                    find_spec = finder.find_spec
                except AttributeError:
                    continue
                spec = find_spec(fullname, list(path) if path is not None else None)

            if spec is not None:
                return spec

        return None

    def _find_path_spec(self, fullname: str, path: ta.Iterable[str]) -> ModuleSpec | None:
        """
        `importlib.machinery.PathFinder._get_spec`, minus `_NamespacePath` (namespace portions are aggregated into a
        plain spec) - path-entry `find_spec` implementations (`FileFinder`, `zipimporter`) are pure lookups.
        """

        namespace_portions: list[str] = []

        for entry in path:
            if not isinstance(entry, str):
                continue

            if (finder := self._path_entry_finder(entry)) is None:
                continue

            try:
                find_spec = finder.find_spec
            except AttributeError:
                continue

            if (spec := find_spec(fullname)) is None:
                continue

            if spec.loader is not None:
                return spec

            if (portions := spec.submodule_search_locations) is not None:
                namespace_portions.extend(portions)

        if namespace_portions:
            spec = ModuleSpec(fullname, None)
            spec.submodule_search_locations = namespace_portions
            return spec

        return None

    def _path_entry_finder(self, entry: str) -> ta.Any:
        if not entry:
            try:
                entry = os.getcwd()
            except OSError:
                return None

        # Read (but never write) the global cache - a custom finder someone installed there should be honored.
        try:
            return sys.path_importer_cache[entry]
        except KeyError:
            pass

        try:
            return self._path_entry_finder_cache[entry]
        except KeyError:
            pass

        finder = None
        for hook in sys.path_hooks:
            try:
                finder = hook(entry)
            except ImportError:
                continue
            break

        self._path_entry_finder_cache[entry] = finder
        return finder

    #

    def _yield_children(self, pkg: Importable) -> ta.Iterator[Importable]:
        if (search := self._live_search_locations(pkg)) is None:
            return

        candidates: set[str] = set()
        for entry in search:
            if not isinstance(entry, str):
                continue
            try:
                candidates.update(self._list_path_entry(entry))
            except Exception:  # noqa
                if self._options.raise_on_failure:
                    raise

        for tail in sorted(candidates):
            child_name = f'{pkg.name}.{tail}' if pkg.name else tail

            try:
                spec = self._find_path_spec(child_name, search)
            except Exception:  # noqa
                if self._options.raise_on_failure:
                    raise
                continue

            if spec is None:
                continue

            yield self._spec_importable(spec)

    def _live_search_locations(self, pkg: Importable) -> ta.Sequence[str] | None:
        """
        Upgrades to the already-imported module's live __path__, but only when it's verifiably the *same* thing that was
        resolved (else a name collision - e.g. enumerating an un-imported pyz containing 'requests' while the real
        'requests' is imported - would silently walk the wrong tree).
        """

        search = pkg.search_locations

        if not pkg.name or (mod := sys.modules.get(pkg.name)) is None:
            return search

        if (mod_path := getattr(mod, '__path__', None)) is None:
            return search

        if pkg.origin is not None:
            if getattr(mod, '__file__', None) != pkg.origin:
                return search
        elif search and not set(mod_path) & set(search):
            return search

        return tuple(mod_path)

    #

    def _list_path_entry(self, entry: str) -> ta.AbstractSet[str]:
        """
        Candidate child names (tails only) present in a path entry. Purely advisory - `_find_path_spec` is the arbiter
        of what each name actually is.
        """

        if os.path.isdir(entry):
            return self._list_dir_entry(entry)

        if (zsp := self._split_zip_path(entry)) is not None:
            return self._list_zip_entry(*zsp)

        return self._list_finder_entry(entry)

    def _list_dir_entry(self, dir_path: str) -> ta.AbstractSet[str]:
        out: set[str] = set()

        with os.scandir(dir_path) as it:
            for de in it:
                if de.is_dir():
                    if de.name not in IGNORED_DIR_NAMES and self._candidate_name_ok(de.name):
                        out.add(de.name)
                elif de.is_file():
                    if (stem := inspect.getmodulename(de.name)) is not None and self._candidate_name_ok(stem):
                        out.add(stem)

        return out

    @staticmethod
    def _split_zip_path(entry: str) -> tuple[str, str] | None:
        """
        Splits a path entry possibly pointing inside a zip archive ('/x/app.pyz/pkg/sub') into (archive_path,
        internal_prefix) the way zipimport does - by walking up until an actual file is hit.
        """

        if not entry:
            return None

        archive = entry
        parts: list[str] = []
        while archive and not os.path.isfile(archive):
            head, tail = os.path.split(archive)
            if head == archive:
                return None
            archive = head
            if tail:
                parts.insert(0, tail)

        if not archive or not zipfile.is_zipfile(archive):
            return None

        return (archive, '/'.join(parts) + '/' if parts else '')

    def _zip_namelist(self, archive: str) -> list[str]:
        try:
            return self._zip_namelist_cache[archive]
        except KeyError:
            pass

        with zipfile.ZipFile(archive) as zf:
            namelist = zf.namelist()

        self._zip_namelist_cache[archive] = namelist
        return namelist

    def _list_zip_entry(self, archive: str, prefix: str) -> ta.AbstractSet[str]:
        out: set[str] = set()

        for zn in self._zip_namelist(archive):
            if prefix:
                if not zn.startswith(prefix):
                    continue
                zn = zn[len(prefix):]
            if not zn:
                continue

            head, sep, _ = zn.partition('/')
            if sep:
                if head not in IGNORED_DIR_NAMES and self._candidate_name_ok(head):
                    out.add(head)
            else:
                if (stem := inspect.getmodulename(head)) is not None and self._candidate_name_ok(stem):
                    out.add(stem)

        return out

    def _list_finder_entry(self, entry: str) -> ta.AbstractSet[str]:
        """
        Fallback for exotic path entry types: the (pkgutil-style) `iter_modules` protocol on whatever path entry finder
        the hooks produce.
        """

        if (finder := self._path_entry_finder(entry)) is None:
            return frozenset()

        if (iter_modules := getattr(finder, 'iter_modules', None)) is None:
            return frozenset()

        return {
            tail
            for name, _ in iter_modules('')
            if self._candidate_name_ok(tail := name.rpartition('.')[2])
        }


##


class ImportlibImportableYielder(ImportableYielder):
    """
    What `traversal.py` did, in backend shape: resolution and traversal actually import every package encountered
    (though not leaf modules), so arbitrary `__init__.py` code runs. Import failures below the root are suppressed
    unless `raise_on_failure`.
    """

    def _import(self, name: str) -> types.ModuleType:
        try:
            return sys.modules[name]
        except KeyError:
            pass

        import importlib
        return importlib.import_module(name)

    def _resolve_root(self, name: str) -> Importable:
        return self._module_importable(name, self._import(name))

    def _yield_children(self, pkg: Importable) -> ta.Iterator[Importable]:
        if pkg.kind == 'module':
            return

        self._import(pkg.name)

        import importlib.resources as importlib_resources
        import pathlib

        for item in importlib_resources.files(pkg.name).iterdir():
            fs_path = str(item) if isinstance(item, pathlib.Path) else None

            if item.is_file():
                if (stem := inspect.getmodulename(item.name)) is not None and self._candidate_name_ok(stem):
                    yield Importable(
                        name=f'{pkg.name}.{stem}',
                        kind='module',
                        origin=fs_path,
                    )

            elif item.is_dir():
                if item.name in IGNORED_DIR_NAMES or not self._candidate_name_ok(item.name):
                    continue

                has_init = any(
                    inspect.getmodulename(child.name) == '__init__'
                    for child in item.iterdir()
                    if child.is_file()
                )

                yield Importable(
                    name=f'{pkg.name}.{item.name}',
                    kind='package' if has_init else 'namespace_package',
                    search_locations=(fs_path,) if fs_path is not None else None,
                )


##


def yield_importable(
        package_root: str,
        *,
        recursive: bool = False,
        filter: ta.Callable[[str], bool] | None = None,  # noqa
        include_special: bool = False,
        raise_on_failure: bool = False,
) -> ta.Iterator[str]:
    """Drop-in equivalent of `traversal.yield_importable` - same signature, same yielded names - but imports nothing."""

    yielder = ZeroImportImportableYielder(YieldImportableOptions(
        recursive=recursive,
        filter=(lambda imp: filter(imp.name)) if filter is not None else None,
        include_special=include_special,
        raise_on_failure=raise_on_failure,
        kinds=frozenset(['module']),
    ))

    for imp in yielder.yield_importable(package_root):
        yield imp.name


def yield_importable_in(
        path_entry: str,
        *,
        recursive: bool = False,
        filter: ta.Callable[[str], bool] | None = None,  # noqa
        include_special: bool = False,
        raise_on_failure: bool = False,
) -> ta.Iterator[str]:
    """
    Like `yield_importable`, but rooted at a path entry - a directory or zip/pyz archive - rather than a named package.
    The entry need not be on sys.path and is never imported; names are relative to it.
    """

    yielder = ZeroImportImportableYielder(YieldImportableOptions(
        recursive=recursive,
        filter=(lambda imp: filter(imp.name)) if filter is not None else None,
        include_special=include_special,
        raise_on_failure=raise_on_failure,
        kinds=frozenset(['module']),
    ))

    for imp in yielder.yield_path_entry(path_entry):
        yield imp.name


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
