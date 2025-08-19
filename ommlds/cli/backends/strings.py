"""
TODO:
 - fix load_manifests already
 - ModelNamePackCollectionThing
"""
import abc
import dataclasses as dc
import os
import typing as ta

from omlish import check
from omlish import lang
from omlish.manifests.globals import GlobalManifestLoader

from ... import minichain as mc
from ...minichain.backends.strings.packs import ModelNameBackendStringPack
from ...minichain.backends.strings.parsing import ParsedBackendString
from ...minichain.backends.strings.parsing import parse_backend_string
from .catalog import BackendCatalog


T = ta.TypeVar('T')


##


def _load_manifests(cls: type[T]) -> ta.Sequence[T]:
    ldr = GlobalManifestLoader.instance()
    pkgs = ldr.scan_or_discover_packages(fallback_root_dir=os.getcwd())  # FIXME
    mfs = ldr.load(*pkgs, only=[cls])
    return [mf.value() for mf in mfs]


##


@dc.dataclass(frozen=True)
class ResolvedBackend:
    backend_name: str
    model_name: str | None = None


class BackendStringResolver(lang.Abstract):
    @abc.abstractmethod
    def resolve_backend_string(self, ps: ParsedBackendString) -> ResolvedBackend | None:
        raise NotImplementedError


class ModelNameBackendStringPackBackendStringResolver(BackendStringResolver):
    def __init__(self, packs: ta.Iterable[ModelNameBackendStringPack]) -> None:
        super().__init__()

        self._packs = list(packs)

    def resolve_backend_string(self, ps: ParsedBackendString) -> ResolvedBackend | None:
        if ps.backend is not None and isinstance(ps.model, ParsedBackendString.NameModel):
            return ResolvedBackend(ps.model.name, ps.model.name)

        for pack in self._packs:
            if ps.backend is not None:
                if ps.backend == pack.backend_name:
                    if isinstance(ps.model, ParsedBackendString.NameModel):
                        return ResolvedBackend(ps.backend, ps.model.name)

                    else:
                        raise NotImplementedError

                else:
                    continue

            if isinstance(ps.model, ParsedBackendString.NameModel):
                if ps.model.name in pack.backend_name:
                    return ResolvedBackend(pack.backend_name, pack.model_names.resolved_default)

                elif ps.model.name == pack.model_names.default:
                    return ResolvedBackend(pack.backend_name, pack.model_names.resolved_default)

                elif ps.model.name in pack.model_names.alias_map:
                    return ResolvedBackend(pack.backend_name, pack.model_names.alias_map[ps.model.name])

            else:
                raise NotImplementedError

        return None


##


class BackendStringBackendCatalog(BackendCatalog):
    def get_backend(self, service_cls: ta.Any, name: str, *args: ta.Any, **kwargs: ta.Any) -> ta.Any:
        ps = parse_backend_string(name)
        rv = ModelNameBackendStringPackBackendStringResolver(_load_manifests(ModelNameBackendStringPack))
        rs = check.not_none(rv.resolve_backend_string(ps))

        return mc.registry_new(
            service_cls,
            rs.backend_name,
            *([mc.ModelName(mn)] if (mn := rs.model_name) is not None else []),
            *args,
            **kwargs,
        )
