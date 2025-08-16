# ruff: noqa: UP006 UP007 UP045
# @omlish-lite
"""
Should be kept somewhat lightweight - used in cli entrypoints.

TODO:
 - persisted caching support - {pkg_name: manifests}
 - real relative cls names - shouldn't need parent package names
 - *require* loaded class names - special All sentinel for explicit all
  - ! late instantiation !
 - per-manifest-item cache?
"""
import dataclasses as dc
import importlib.machinery
import importlib.resources
import importlib.util
import json
import os.path
import threading
import typing as ta

from .types import Manifest


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
            [(cls_key, value_dct)] = self._manifest.value.items()
            return cls_key

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

    def __init__(
            self,
            *,
            module_remap: ta.Optional[ta.Mapping[str, str]] = None,
            value_instantiator: ta.Optional[ta.Callable[..., ta.Any]] = None,
    ) -> None:
        super().__init__()

        self._value_instantiator = value_instantiator
        self._module_remap = module_remap or {}

        self._lock = threading.RLock()

        self._module_reverse_remap = {v: k for k, v in self._module_remap.items()}

        self._loaded_classes: ta.Dict[str, type] = {}
        self._loaded_packages: ta.Dict[str, ta.Optional[ManifestLoader.LoadedPackage]] = {}

        self._scanned_package_root_dirs: ta.Dict[str, ta.Sequence[str]] = {}

    #

    @classmethod
    def kwargs_from_entry_point(
            cls,
            globals: ta.Mapping[str, ta.Any],  # noqa
            *,
            module_remap: ta.Optional[ta.Mapping[str, str]] = None,
            **kwargs: ta.Any,
    ) -> ta.Dict[str, ta.Any]:
        rm: ta.Dict[str, str] = {}

        if module_remap:
            rm.update(module_remap)

        if '__name__' in globals and '__spec__' in globals:
            name: str = globals['__name__']
            spec: importlib.machinery.ModuleSpec = globals['__spec__']
            if '__main__' not in rm and name == '__main__':
                rm[spec.name] = '__main__'

        return dict(module_remap=rm, **kwargs)

    #

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

    #

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

        t = importlib.resources.files(pkg_name).joinpath(file_name)
        if not t.is_file():
            return None
        return t.read_text('utf-8')

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

    #

    def _instantiate_value(self, cls: type, **kwargs: ta.Any) -> ta.Any:
        if self._value_instantiator is not None:
            return self._value_instantiator(cls, **kwargs)
        else:
            return cls(**kwargs)

    def _instantiate_loaded_manifest(self, ld_man: LoadedManifest) -> ta.Any:
        [(cls_key, value_dct)] = ld_man.manifest.value.items()
        cls = self._load_class(cls_key)
        value = self._instantiate_value(cls, **value_dct)
        return value

    #

    class LOAD_ALL:  # noqa
        def __new__(cls, *args, **kwargs):  # noqa
            raise TypeError

        def __init_subclass__(cls, **kwargs):  # noqa
            raise TypeError

    def _load(
            self,
            *pkg_names: str,
            only: ta.Optional[ta.Iterable[type]] = None,
    ) -> ta.Sequence[LoadedManifest]:
        only_keys: ta.Optional[ta.Set]
        if only is not None:
            only_keys = set()
            for cls in only:
                if not (isinstance(cls, type) and dc.is_dataclass(cls)):
                    raise TypeError(cls)
                mod_name = cls.__module__
                mod_name = self._module_reverse_remap.get(mod_name, mod_name)
                only_keys.add(f'${mod_name}.{cls.__qualname__}')
        else:
            only_keys = None

        lst: ta.List[ManifestLoader.LoadedManifest] = []
        for pn in pkg_names:
            lp = self.load_package(pn)
            if lp is None:
                continue

            for m in lp.manifests:
                if only_keys is not None and m.class_key not in only_keys:
                    continue

                lst.append(m)

        return lst

    def load(
            self,
            *pkg_names: str,
            only: ta.Optional[ta.Iterable[type]] = None,
    ) -> ta.Sequence[LoadedManifest]:
        with self._lock:
            return self._load(
                *pkg_names,
                only=only,
            )

    #

    ENTRY_POINT_GROUP: ta.ClassVar[str] = 'omlish.manifests'

    _discovered_packages: ta.ClassVar[ta.Optional[ta.Sequence[str]]] = None

    @classmethod
    def discover_packages(cls) -> ta.Sequence[str]:
        if (x := cls._discovered_packages) is not None:
            return x

        # This is a fat dep so do it late.
        from importlib import metadata as importlib_metadata  # noqa

        x = [
            ep.value
            for ep in importlib_metadata.entry_points(group=cls.ENTRY_POINT_GROUP)
        ]

        cls._discovered_packages = x
        return x

    #

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

    def scan_or_discover_packages(
            self,
            *,
            specified_root_dirs: ta.Optional[ta.Sequence[str]] = None,
            fallback_root_dir: ta.Optional[str] = None,
    ) -> ta.Sequence[str]:
        pkgs: list[str] = []

        if specified_root_dirs is not None:
            if isinstance(specified_root_dirs, str):
                raise TypeError(specified_root_dirs)

            for r in specified_root_dirs:
                pkgs.extend(self._scan_package_root_dir(r))

        else:
            pkgs.extend(self.discover_packages())

            if not pkgs and fallback_root_dir is not None:
                pkgs.extend(self._scan_package_root_dir(fallback_root_dir))

        return pkgs
