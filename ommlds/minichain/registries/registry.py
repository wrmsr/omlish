"""
TODO:
 - queue register_types + late load manifests ? less urgent than late loading marshal lol
"""
import sys
import threading
import typing as ta

from omlish import check
from omlish import collections as col
from omlish import dataclasses as dc

from .manifests import RegistryManifest
from .manifests import RegistryTypeManifest


T = ta.TypeVar('T')
U = ta.TypeVar('U')


##


class Registry:
    def __init__(
            self,
            registry_type_manifests: ta.Iterable[RegistryTypeManifest],
            registry_manifests: ta.Iterable[RegistryManifest],
    ) -> None:
        super().__init__()

        self._lock = threading.RLock()

        self._registry_type_manifests = list(registry_type_manifests)
        self._registry_manifests = list(registry_manifests)

        self._registry_type_manifests_by_name = col.make_map(
            ((m.attr, m) for m in self._registry_type_manifests),
            strict=True,
        )

        self._modules: dict[str, Registry._Module] = {}
        for rtm in self._registry_type_manifests:
            m = self._get_module(rtm.module)
            m.registry_type_manifests.append(rtm)
            m.unresolved_type_manifests.append(rtm)

        self._registry_manifests_by_name_by_type = {
            t: RegistryManifest.build_name_dict(l)
            for t, l in col.multi_map((m.type, m) for m in self._registry_manifests).items()
        }

        self._registry_type_cls_by_name: dict[str, type] = {}
        self._registry_cls_by_name_by_type_name: dict[str, dict[str, type]] = {}

        self._registered_types: dict[ta.Any, Registry._RegisteredType] = {}
        self._resolved_registry_type_names_by_registered_type: dict[ta.Any, str] = {}

    #

    @dc.dataclass()
    class _Module:
        name: str

        registry_type_manifests: list[RegistryTypeManifest] = dc.field(default_factory=list)

        unresolved_type_manifests: list[RegistryTypeManifest] = dc.field(default_factory=list)

    def _get_module(self, name: str) -> _Module:
        try:
            return self._modules[name]
        except KeyError:
            pass
        m = self._modules[name] = Registry._Module(name)
        return m

    #

    @dc.dataclass(frozen=True)
    class _RegisteredType:
        cls: ta.Any

        _: dc.KW_ONLY

        module: str | None = None

    def register_type(
            self,
            cls: ta.Any,
            *,
            module: str | None = None,
    ) -> None:
        with self._lock:
            if cls in self._registered_types:
                raise RuntimeError(f'Type {cls} already registered')

            self._registered_types[cls] = Registry._RegisteredType(
                cls,
                module=module,
            )

            if module is not None:
                mo = sys.modules[module]
                m = self._get_module(module)

                nu: list[RegistryTypeManifest] = []
                for rtm in m.unresolved_type_manifests:
                    if hasattr(mo, rtm.attr) and (v := getattr(mo, rtm.attr)) is cls:
                        check.not_in(v, self._resolved_registry_type_names_by_registered_type)
                        self._resolved_registry_type_names_by_registered_type[v] = rtm.attr
                    else:
                        nu.append(rtm)
                m.unresolved_type_manifests = nu

    #

    def get_registry_type_cls(self, name: str) -> type:
        with self._lock:
            try:
                return self._registry_type_cls_by_name[name]
            except KeyError:
                pass

            m = self._registry_type_manifests_by_name[name]
            cls = m.resolve()
            self._registry_type_cls_by_name[name] = cls
            return cls

    def get_registry_cls(self, selector: ta.Any, name: str) -> type:
        with self._lock:
            if isinstance(selector, str):
                type_name = check.in_(selector, self._registry_type_manifests_by_name)
            elif isinstance(selector, type):
                type_name = selector.__name__
            else:
                type_name = self._resolved_registry_type_names_by_registered_type[selector]

            try:
                d = self._registry_cls_by_name_by_type_name[type_name]
            except KeyError:
                d = self._registry_cls_by_name_by_type_name[type_name] = {}

            try:
                return d[name]
            except KeyError:
                pass

            m = self._registry_manifests_by_name_by_type[type_name][name]
            cls = m.resolve()
            d[name] = cls

            return cls
