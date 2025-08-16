"""
TODO:
 - fix load_manifests already
 - ModelNamePackCollectionThing
"""
import dataclasses as dc
import os
import typing as ta

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


@dc.dataclass(frozen=True)
class Resolved:
    backend_name: str
    model_name: str | None = None


def resolve(ps: ParsedBackendString) -> Resolved:
    if ps.backend is not None and isinstance(ps.model, ParsedBackendString.NameModel):
        return Resolved(ps.model.name, ps.model.name)

    packs = _load_manifests(ModelNameBackendStringPack)
    for pack in packs:
        if ps.backend is not None:
            if ps.backend == pack.backend_name:
                if isinstance(ps.model, ParsedBackendString.NameModel):
                    return Resolved(ps.backend, ps.model.name)

                else:
                    raise NotImplementedError

            else:
                continue

        if isinstance(ps.model, ParsedBackendString.NameModel):
            if ps.model.name in pack.backend_name:
                return Resolved(pack.backend_name, pack.model_names.resolved_default)

            elif ps.model.name == pack.model_names.default:
                return Resolved(pack.backend_name, pack.model_names.resolved_default)

            elif ps.model.name in pack.model_names.alias_map:
                return Resolved(pack.backend_name, pack.model_names.alias_map[ps.model.name])

        else:
            raise NotImplementedError

    raise NotImplementedError


class BackendStringBackendCatalog(BackendCatalog):
    def get_backend(self, service_cls: ta.Any, name: str, *args: ta.Any, **kwargs: ta.Any) -> ta.Any:
        ps = parse_backend_string(name)
        rs = resolve(ps)

        return mc.registry_new(
            service_cls,
            rs.backend_name,
            *([mc.ModelName(mn)] if (mn := rs.model_name) is not None else []),
            *args,
            **kwargs,
        )
