# ruff: noqa: UP006 UP007 UP045
# @omlish-lite
"""
Should be kept somewhat lightweight - used in cli entrypoints.

TODO:
 - real relative cls names - shouldn't need parent package names
 - TypeMap style weak cache of issubclass queries
  - wait.. lazily load the class for virtual subclass queries? xor support virtual bases?
 - weakref class dict keys?
 - cheap_discover_package_root_dirs: Seq[str] | None = None or smth
 - maaaybe.. add an EnvVar? OMLISH_MANIFEST_ROOT_DIRS? if set to : delimited, turns off package disco and overrides
   scan_root_dirs
  - currently the cli cant subprocess itself and keep manifests working
  - EnvVar cls is already lite
 - can discover_packages deadlock with concurrent / multithreaded imports?
"""
import dataclasses as dc
import importlib.machinery
import importlib.util
import json
import os.path
import threading
import typing as ta

from .types import Manifest


T = ta.TypeVar('T')


##


class ManifestLoader:
    class LoadedManifest:
        def __init__(
                self,
                package: 'ManifestLoader.LoadedPackage',
                resolved: 'ManifestLoader._ResolvedManifest',
        ) -> None:
            super().__init__()

            self._package = package
            self._resolved = resolved

        def __repr__(self) -> str:
            return (
                f'{self.__class__.__name__}@{id(self):x}('
                f'package={self._package.name!r}, '
                f'module={self._resolved.module!r}, '
                f'class_key={self._resolved.class_key!r}'
                f')'
            )

        @property
        def package(self) -> 'ManifestLoader.LoadedPackage':
            return self._package

        @property
        def module(self) -> str:
            return self._resolved.module

        @property
        def class_key(self) -> str:
            return self._resolved.class_key

        @property
        def manifest(self) -> Manifest:
            return self._resolved.manifest

        @property
        def loader(self) -> 'ManifestLoader':
            return self._package.loader

        _value: ta.Any

        def value(self) -> ta.Any:
            try:
                return self._value
            except AttributeError:
                pass

            value = self.loader._instantiate_resolved_manifest(self._resolved)  # noqa
            self._value = value
            return value

    class LoadedPackage:
        def __init__(
                self,
                loader: 'ManifestLoader',
                name: str,
        ) -> None:
            super().__init__()

            self._loader = loader
            self._name = name

        _manifests: ta.Sequence['ManifestLoader.LoadedManifest']

        def __repr__(self) -> str:
            return f'{self.__class__.__name__}@{id(self):x}(name={self._name!r})'

        @property
        def loader(self) -> 'ManifestLoader':
            return self._loader

        @property
        def name(self) -> str:
            return self._name

        @property
        def manifests(self) -> ta.Sequence['ManifestLoader.LoadedManifest']:
            return self._manifests

        _manifests_by_class_key: ta.Mapping[str, ta.Sequence['ManifestLoader.LoadedManifest']]

        @property
        def manifests_by_class_key(self) -> ta.Mapping[str, ta.Sequence['ManifestLoader.LoadedManifest']]:
            try:
                return self._manifests_by_class_key
            except AttributeError:
                pass

            dct: dict = {}
            for m in self._manifests:
                try:
                    lst = dct[m.class_key]
                except KeyError:
                    lst = dct[m.class_key] = []
                lst.append(m)
            self._manifests_by_class_key = dct
            return dct

    ##

    @dc.dataclass(frozen=True)
    class Config:
        package_scan_root_dirs: ta.Optional[ta.Collection[str]] = None

        discover_packages: ta.Optional[bool] = None
        discover_packages_fallback_scan_root_dirs: ta.Optional[ta.Collection[str]] = None

        module_remap: ta.Optional[ta.Mapping[str, str]] = None

        value_instantiator: ta.Optional[ta.Callable[..., ta.Any]] = None

        def __post_init__(self) -> None:
            if isinstance(self.package_scan_root_dirs, str):
                raise TypeError(self.package_scan_root_dirs)
            if isinstance(self.discover_packages_fallback_scan_root_dirs, bool):
                raise TypeError(self.discover_packages_fallback_scan_root_dirs)

        @classmethod
        def merge(cls, *configs: 'ManifestLoader.Config') -> 'ManifestLoader.Config':
            kw: dict = {}
            for c in configs:
                for k, v in dc.asdict(c).items():
                    if v is None:
                        continue
                    elif k in ('package_scan_root_dirs', 'discover_packages_fallback_scan_root_dirs'):  # noqa
                        kw[k] = [*kw.get(k, []), *v]
                    elif k == 'module_remap':
                        kw[k] = {**kw.get(k, {}), **v}
                    else:
                        kw[k] = v
            return cls(**kw)

        def __or__(self, other: 'ManifestLoader.Config') -> 'ManifestLoader.Config':
            return ManifestLoader.Config.merge(self, other)

    def __init__(
            self,
            config: Config,
    ) -> None:
        super().__init__()

        self._config = config

        self._lock = threading.RLock()

        self._module_remap = config.module_remap or {}
        self._module_reverse_remap = {v: k for k, v in (self._module_remap or {}).items()}

        self._loaded_classes: ta.Dict[str, type] = {}
        self._loaded_packages: ta.Dict[str, ta.Optional[ManifestLoader.LoadedPackage]] = {}

        self._scanned_package_root_dirs: ta.Dict[str, ta.Sequence[str]] = {}

    @property
    def config(self) -> Config:
        return self._config

    @classmethod
    def config_from_entry_point(
            cls,
            globals: ta.Mapping[str, ta.Any],  # noqa
    ) -> Config:
        rm: ta.Dict[str, str] = {}

        if '__name__' in globals and '__spec__' in globals:
            name: str = globals['__name__']
            spec: importlib.machinery.ModuleSpec = globals['__spec__']
            if '__main__' not in rm and name == '__main__':
                rm[spec.name] = '__main__'

        return ManifestLoader.Config(module_remap=rm)

    ##

    ENTRY_POINT_GROUP: ta.ClassVar[str] = 'omlish.manifests'

    _discovered_packages: ta.ClassVar[ta.Optional[ta.Sequence[str]]] = None

    @classmethod
    def _discover_packages_uncached(cls) -> ta.Sequence[str]:
        from importlib import metadata as importlib_metadata  # noqa

        return [
            ep.value
            for ep in importlib_metadata.entry_points(group=cls.ENTRY_POINT_GROUP)
        ]

    @classmethod
    def discover_packages(cls) -> ta.Sequence[str]:
        if (x := cls._discovered_packages) is not None:
            return x

        x = cls._discover_packages_uncached()
        cls._discovered_packages = x
        return x

    ##

    def _scan_package_root_dir_uncached(
            self,
            root_dir: str,
    ) -> ta.Sequence[str]:
        pkgs: ta.List[str] = []

        for n in os.listdir(root_dir):
            if (
                    os.path.isdir(p := os.path.join(root_dir, n)) and
                    os.path.exists(os.path.join(p, '__init__.py'))
            ):
                pkgs.append(n)

        return pkgs

    def _scan_package_root_dir_locked(
            self,
            root_dir: str,
    ) -> ta.Sequence[str]:
        try:
            return self._scanned_package_root_dirs[root_dir]
        except KeyError:
            pass

        ret = self._scan_package_root_dir_uncached(root_dir)
        self._scanned_package_root_dirs[root_dir] = ret
        return ret

    def _scan_package_root_dir(
            self,
            root_dir: str,
    ) -> ta.Sequence[str]:
        with self._lock:
            return self._scan_package_root_dir_locked(root_dir)

    ##

    def _detect_packages_uncached(self) -> ta.AbstractSet[str]:
        ret: ta.Set[str] = set()

        for r in self._config.package_scan_root_dirs or []:
            ret.update(self._scan_package_root_dir_locked(r))

        if self._config.discover_packages:
            ret.update(dps := self.discover_packages())
            if not dps:
                for r in self._config.discover_packages_fallback_scan_root_dirs or []:
                    ret.update(self._scan_package_root_dir_locked(r))

        return ret

    _detected_packages: ta.Optional[ta.AbstractSet[str]] = None

    def _detect_packages_locked(self) -> ta.AbstractSet[str]:
        if self._detected_packages is None:
            self._detected_packages = self._detect_packages_uncached()

        return self._detected_packages

    def detect_packages(self) -> ta.AbstractSet[str]:
        with self._lock:
            return self._detect_packages_locked()

    ##

    @dc.dataclass()
    class ClassKeyError(Exception):
        key: str
        module: ta.Optional[str] = None

    def _load_class_uncached(self, key: str) -> type:
        if not key.startswith('!'):
            raise ManifestLoader.ClassKeyError(key)

        parts = key[1:].split('.')
        if '' in parts:
            raise ManifestLoader.ClassKeyError(key)

        pos = next(i for i, p in enumerate(parts) if p[0].isupper())

        mod_name = '.'.join(parts[:pos])
        mod_name = self._module_remap.get(mod_name, mod_name)
        mod = importlib.import_module(mod_name)

        obj: ta.Any = mod
        for ca in parts[pos:]:
            obj = getattr(obj, ca)

        cls = obj
        if not isinstance(cls, type):
            raise TypeError(cls)

        return cls

    def _load_class_locked(self, key: str) -> type:
        try:
            return self._loaded_classes[key]
        except KeyError:
            pass

        cls = self._load_class_uncached(key)
        self._loaded_classes[key] = cls
        return cls

    def _load_class(self, key: str) -> type:
        with self._lock:
            return self._load_class_locked(key)

    def get_class_key(self, cls: type) -> str:
        if not (isinstance(cls, type) and dc.is_dataclass(cls)):
            raise TypeError(cls)
        mod_name = cls.__module__
        mod_name = self._module_reverse_remap.get(mod_name, mod_name)
        return f'!{mod_name}.{cls.__qualname__}'

    ##

    class _ResolvedManifest(ta.NamedTuple):
        manifest: Manifest
        package: str

        module: str
        class_key: str
        value_dct: ta.Any

    @classmethod
    def _resolve_raw_manifest(
            cls,
            m: Manifest,
            *,
            package_name: str,
    ) -> _ResolvedManifest:
        # self._module = module
        # self._class_key = class_key
        if not m.module.startswith('.'):
            raise NameError(m.module)

        module = package_name + m.module

        [(class_key, value_dct)] = m.value.items()

        if not class_key.startswith('!'):
            raise ManifestLoader.ClassKeyError(class_key, module=module)

        if class_key.startswith('!.'):
            class_key = f'!{package_name}{class_key[1:]}'

        # FIXME: move to builder
        # elif key.startswith('$.'):
        #     if module.startswith('.'):
        #         raise NameError(module)
        #     kl = key[1:].split('.')
        #     ml = module.split('.')
        #     lvl = len(kl) - kl[::-1].index('')
        #     if lvl >= len(ml):
        #         raise ManifestLoader.ClassKeyError(key, module=module)
        #     rn = '.'.join([*ml[:-lvl], *kl[lvl:]])
        #     return f'${rn}'

        return ManifestLoader._ResolvedManifest(
            manifest=m,
            package=package_name,

            module=module,
            class_key=class_key,
            value_dct=value_dct,
        )

    ##

    @classmethod
    def _deserialize_raw_manifests(cls, obj: ta.Any) -> ta.Sequence[Manifest]:
        if not isinstance(obj, (list, tuple)):
            raise TypeError(obj)

        lst: ta.List[Manifest] = []
        for e in obj:
            lst.append(Manifest(**e))

        return lst

    @classmethod
    def _read_package_file_text(cls, package_name: str, file_name: str) -> ta.Optional[str]:
        # importlib.resources.files actually imports the package - to avoid this, if possible, the file is read straight
        # off the filesystem.
        # FIXME: find_spec *still* imports the parent package to get __path__ to feed to _find_spec...
        spec = importlib.util.find_spec(package_name)
        if (
                spec is not None and
                isinstance(spec.loader, importlib.machinery.SourceFileLoader) and
                spec.origin is not None and
                len(spec.submodule_search_locations or []) == 1 and
                os.path.basename(spec.origin) == '__init__.py' and
                os.path.isfile(spec.origin)
        ):
            file_path = os.path.join(os.path.dirname(spec.origin), file_name)
            if os.path.isfile(file_path):
                with open(file_path, encoding='utf-8') as f:
                    return f.read()

        from importlib import resources as importlib_resources  # noqa

        t = importlib_resources.files(package_name).joinpath(file_name)
        if not t.is_file():
            return None
        return t.read_text('utf-8')

    MANIFESTS_FILE_NAME: ta.ClassVar[str] = '.omlish-manifests.json'

    @classmethod
    def _read_package_raw_manifests(cls, package_name: str) -> ta.Optional[ta.Sequence[Manifest]]:
        src = cls._read_package_file_text(package_name, cls.MANIFESTS_FILE_NAME)
        if src is None:
            return None

        obj = json.loads(src)
        if not isinstance(obj, (list, tuple)):
            raise TypeError(obj)

        return cls._deserialize_raw_manifests(obj)

    ##

    def _load_package_uncached(self, package_name: str) -> ta.Optional[LoadedPackage]:
        if (raw_lst := self._read_package_raw_manifests(package_name)) is None:
            return None

        ld_pkg = ManifestLoader.LoadedPackage(self, package_name)

        ld_man_lst: ta.List[ManifestLoader.LoadedManifest] = []
        for raw in raw_lst:
            rsv = self._resolve_raw_manifest(raw, package_name=package_name)

            ld_man = ManifestLoader.LoadedManifest(ld_pkg, rsv)

            ld_man_lst.append(ld_man)

        ld_pkg._manifests = ld_man_lst  # noqa

        return ld_pkg

    def _load_package_locked(self, package_name: str) -> ta.Optional[LoadedPackage]:
        try:
            return self._loaded_packages[package_name]
        except KeyError:
            pass

        pkg = self._load_package_uncached(package_name)
        self._loaded_packages[package_name] = pkg
        return pkg

    def load_package(self, package_name: str) -> ta.Optional[LoadedPackage]:
        with self._lock:
            return self._load_package_locked(package_name)

    ##

    def _instantiate_value(self, cls: type, **kwargs: ta.Any) -> ta.Any:
        if self._config.value_instantiator is not None:
            return self._config.value_instantiator(cls, **kwargs)
        else:
            return cls(**kwargs)

    def _instantiate_resolved_manifest(self, resolved: _ResolvedManifest) -> ta.Any:
        cls = self._load_class(resolved.class_key)
        value = self._instantiate_value(cls, **resolved.value_dct)
        return value

    ##

    def _load_locked(
            self,
            *,
            packages: ta.Optional[ta.Collection[str]] = None,
            classes: ta.Optional[ta.Collection[type]] = None,
    ) -> ta.Sequence[LoadedManifest]:
        if isinstance(packages, str):
            raise TypeError(packages)

        class_keys: ta.Optional[ta.Set[str]] = None
        if classes is not None:
            class_keys = {self.get_class_key(cls) for cls in classes}

        if packages is None:
            packages = self._detect_packages_locked()

        lst: ta.List[ManifestLoader.LoadedManifest] = []
        for pn in packages:
            if (lp := self._load_package_locked(pn)) is None:
                continue

            if class_keys is not None:
                for ck in class_keys:
                    lst.extend(lp.manifests_by_class_key.get(ck, []))

            else:
                lst.extend(lp.manifests)

        return lst

    def load(
            self,
            *,
            packages: ta.Optional[ta.Collection[str]] = None,
            classes: ta.Optional[ta.Collection[type]] = None,
    ) -> ta.Sequence[LoadedManifest]:
        if isinstance(packages, str):
            raise TypeError(packages)

        with self._lock:
            return self._load_locked(
                packages=packages,
                classes=classes,
            )

    def load_values(
            self,
            *,
            packages: ta.Optional[ta.Collection[str]] = None,
            classes: ta.Optional[ta.Collection[type]] = None,
    ) -> ta.Sequence[ta.Any]:
        return [
            lm.value()
            for lm in self.load(
                packages=packages,
                classes=classes,
            )
        ]

    def load_values_of(
            self,
            cls: ta.Type[T],
            *,
            packages: ta.Optional[ta.Collection[str]] = None,
    ) -> ta.Sequence[T]:
        return [
            ta.cast(T, lm.value())
            for lm in self.load(
                packages=packages,
                classes=[cls],
            )
        ]
