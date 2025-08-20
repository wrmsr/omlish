# ruff: noqa: UP006 UP007 UP045
# @omlish-lite
"""
Should be kept somewhat lightweight - used in cli entrypoints.

TODO:
 - persisted caching support - {pkg_name: manifests}
 - real relative cls names - shouldn't need parent package names
 - *require* loaded class names - special All sentinel for explicit all
  - ! late instantiation !
 - TypeMap style weak cache of issubclass queries
  - wait.. lazily load the class for virtual subclass queries? xor support virtual bases?
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
                manifest: Manifest,
        ) -> None:
            super().__init__()

            self._package = package
            self._manifest = manifest

            [(cls_key, value_dct)] = self._manifest.value.items()  # noqa
            self._cls_key = cls_key

        @property
        def package(self) -> 'ManifestLoader.LoadedPackage':
            return self._package

        @property
        def manifest(self) -> Manifest:
            return self._manifest

        @property
        def loader(self) -> 'ManifestLoader':
            return self._package.loader

        @property
        def class_key(self) -> str:
            return self._cls_key

        _value: ta.Any

        def value(self) -> ta.Any:
            try:
                return self._value
            except AttributeError:
                pass

            value = self.loader._instantiate_loaded_manifest(self)  # noqa
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

    _detected_packages: ta.Set[str]

    def _do_initialize(self) -> None:
        self._detected_packages = set()

        for r in self._config.package_scan_root_dirs or []:
            self._detected_packages.update(self._scan_package_root_dir_locked(r))

        if self._config.discover_packages:
            self._detected_packages.update(dps := self.discover_packages())
            if not dps:
                for r in self._config.discover_packages_fallback_scan_root_dirs or []:
                    self._detected_packages.update(self._scan_package_root_dir_locked(r))

    _has_initialized = False

    def _initialize_locked(self) -> None:
        if not self._has_initialized:
            self._do_initialize()
            self._has_initialized = True

    def has_initialized(self) -> bool:
        with self._lock:
            return self._has_initialized

    def initialize(self) -> None:
        if not self._has_initialized:
            with self._lock:
                self._initialize_locked()

    ##

    def _load_class_uncached(self, key: str) -> type:
        if not key.startswith('$'):
            raise Exception(f'Bad key: {key}')

        parts = key[1:].split('.')
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
        return f'${mod_name}.{cls.__qualname__}'

    ##

    def _deserialize_raw_manifests(self, obj: ta.Any, pkg_name: str) -> ta.Sequence[Manifest]:
        if not isinstance(obj, (list, tuple)):
            raise TypeError(obj)

        lst: ta.List[Manifest] = []
        for e in obj:
            m = Manifest(**e)

            m = dc.replace(m, module=pkg_name + m.module)

            [(key, value_dct)] = m.value.items()
            if not key.startswith('$'):
                raise Exception(f'Bad key: {key}')
            if key.startswith('$.'):
                key = f'${pkg_name}{key[1:]}'
                m = dc.replace(m, value={key: value_dct})

            lst.append(m)

        return lst

    #

    def _read_package_file_text(self, pkg_name: str, file_name: str) -> ta.Optional[str]:
        # importlib.resources.files actually imports the package - to avoid this, if possible, the file is read straight
        # off the filesystem.
        spec = importlib.util.find_spec(pkg_name)
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
        t = importlib_resources.files(pkg_name).joinpath(file_name)
        if not t.is_file():
            return None
        return t.read_text('utf-8')

    #

    MANIFESTS_FILE_NAME: ta.ClassVar[str] = '.manifests.json'

    def _load_package_uncached(self, pkg_name: str) -> ta.Optional[LoadedPackage]:
        src = self._read_package_file_text(pkg_name, self.MANIFESTS_FILE_NAME)
        if src is None:
            return None

        obj = json.loads(src)
        if not isinstance(obj, (list, tuple)):
            raise TypeError(obj)

        raw_lst = self._deserialize_raw_manifests(obj, pkg_name)

        ld_pkg = ManifestLoader.LoadedPackage(self, pkg_name)

        ld_man_lst: ta.List[ManifestLoader.LoadedManifest] = []
        for raw in raw_lst:
            ld_man = ManifestLoader.LoadedManifest(ld_pkg, raw)

            ld_man_lst.append(ld_man)

        ld_pkg._manifests = ld_man_lst  # noqa

        return ld_pkg

    def _load_package_locked(self, pkg_name: str) -> ta.Optional[LoadedPackage]:
        try:
            return self._loaded_packages[pkg_name]
        except KeyError:
            pass

        pkg = self._load_package_uncached(pkg_name)
        self._loaded_packages[pkg_name] = pkg
        return pkg

    def load_package(self, pkg_name: str) -> ta.Optional[LoadedPackage]:
        with self._lock:
            return self._load_package_locked(pkg_name)

    ##

    def _instantiate_value(self, cls: type, **kwargs: ta.Any) -> ta.Any:
        if self._config.value_instantiator is not None:
            return self._config.value_instantiator(cls, **kwargs)
        else:
            return cls(**kwargs)

    def _instantiate_loaded_manifest(self, ld_man: LoadedManifest) -> ta.Any:
        [(cls_key, value_dct)] = ld_man.manifest.value.items()
        cls = self._load_class(cls_key)
        value = self._instantiate_value(cls, **value_dct)
        return value

    ##

    def _load_initialized(
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
            packages = self._detected_packages

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

    def _load_locked(
            self,
            *,
            packages: ta.Optional[ta.Collection[str]] = None,
            classes: ta.Optional[ta.Collection[type]] = None,
    ) -> ta.Sequence[LoadedManifest]:
        self._initialize_locked()
        return self._load_initialized(
            packages=packages,
            classes=classes,
        )

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
