"""
Should be kept somewhat lightweight - used in cli entrypoints.

TODO:
 - persisted caching support - {pkg_name: manifests}
"""
# ruff: noqa: UP006 UP007
import dataclasses as dc
import importlib.machinery
import importlib.resources
import json
import typing as ta

from .types import Manifest


##


class ManifestLoader:
    def __init__(
            self,
            *,
            module_remap: ta.Optional[ta.Mapping[str, str]] = None,
    ) -> None:
        super().__init__()

        self._module_remap = module_remap or {}
        self._module_reverse_remap = {v: k for k, v in self._module_remap.items()}

        self._cls_cache: ta.Dict[str, type] = {}
        self._raw_cache: ta.Dict[str, ta.Optional[ta.Sequence[Manifest]]] = {}

    @classmethod
    def from_entry_point(
            cls,
            globals: ta.Mapping[str, ta.Any],  # noqa
            *,
            module_remap: ta.Optional[ta.Mapping[str, str]] = None,
            **kwargs: ta.Any,
    ) -> 'ManifestLoader':
        rm: ta.Dict[str, str] = {}

        if module_remap:
            rm.update(module_remap)

        if '__name__' in globals and '__spec__' in globals:
            name: str = globals['__name__']
            spec: importlib.machinery.ModuleSpec = globals['__spec__']
            if '__main__' not in rm and name == '__main__':
                rm[spec.name] = '__main__'

        return cls(module_remap=rm, **kwargs)

    def load_cls(self, key: str) -> type:
        try:
            return self._cls_cache[key]
        except KeyError:
            pass

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

        self._cls_cache[key] = cls
        return cls

    def load_contents(self, obj: ta.Any, pkg_name: str) -> ta.Sequence[Manifest]:
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

    def load_raw(self, pkg_name: str) -> ta.Optional[ta.Sequence[Manifest]]:
        try:
            return self._raw_cache[pkg_name]
        except KeyError:
            pass

        t = importlib.resources.files(pkg_name).joinpath('.manifests.json')
        if not t.is_file():
            self._raw_cache[pkg_name] = None
            return None

        src = t.read_text('utf-8')
        obj = json.loads(src)
        if not isinstance(obj, (list, tuple)):
            raise TypeError(obj)

        lst = self.load_contents(obj, pkg_name)

        self._raw_cache[pkg_name] = lst
        return lst

    def load(
            self,
            *pkg_names: str,
            only: ta.Optional[ta.Iterable[type]] = None,
    ) -> ta.Sequence[Manifest]:
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

        lst: ta.List[Manifest] = []
        for pn in pkg_names:
            for manifest in (self.load_raw(pn) or []):
                [(key, value_dct)] = manifest.value.items()
                if only_keys is not None and key not in only_keys:
                    continue

                cls = self.load_cls(key)
                value = cls(**value_dct)

                manifest = dc.replace(manifest, value=value)
                lst.append(manifest)

        return lst

    ENTRY_POINT_GROUP = 'omlish.manifests'

    def discover(self) -> ta.Sequence[str]:
        # This is a fat dep so do it late.
        import importlib.metadata

        return [
            ep.value
            for ep in importlib.metadata.entry_points(group=self.ENTRY_POINT_GROUP)
        ]
