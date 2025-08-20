"""
TODO:
 - fix load_manifests already
 - ModelNamePackCollectionThing
"""
import abc
import dataclasses as dc
import typing as ta

from omlish import check
from omlish import lang
from omlish.manifests.globals import GlobalManifestLoader

from ... import minichain as mc
from ...minichain.backends.strings.manifests import BackendStringsManifest
from ...minichain.backends.strings.parsing import ParsedBackendString
from ...minichain.backends.strings.parsing import parse_backend_string
from .catalog import BackendCatalog


T = ta.TypeVar('T')


##


@dc.dataclass(frozen=True)
class ResolvedBackend:
    backend_name: str

    args: ta.Sequence[ta.Any] | None = None


class BackendStringResolver(lang.Abstract):
    @abc.abstractmethod
    def resolve_backend_string(self, ps: ParsedBackendString) -> ResolvedBackend | None:
        raise NotImplementedError


##


class ManifestBackendStringResolver(BackendStringResolver):
    def __init__(self, manifests: ta.Iterable[BackendStringsManifest]) -> None:
        super().__init__()

        self._manifests = list(manifests)

    def _model_name_args(self, s: str | None) -> ta.Sequence[ta.Any]:
        if s is not None:
            return [mc.ModelName(s)]
        else:
            return []

    def resolve_backend_string(self, ps: ParsedBackendString) -> ResolvedBackend | None:
        if ps.backend is not None and isinstance(ps.model, ParsedBackendString.NameModel):
            return ResolvedBackend(
                ps.model.name,
                self._model_name_args(ps.model.name),
            )

        for m in self._manifests:
            if ps.backend is not None:
                if ps.backend == m.backend_name:
                    if isinstance(ps.model, ParsedBackendString.NameModel):
                        return ResolvedBackend(
                            ps.backend,
                            self._model_name_args(ps.model.name),
                        )

                    else:
                        raise NotImplementedError

                else:
                    continue

            if isinstance(ps.model, ParsedBackendString.NameModel):
                if ps.model.name in m.backend_name:
                    return ResolvedBackend(
                        m.backend_name,
                        self._model_name_args(m.model_names.resolved_default if m.model_names is not None else None),
                    )

                if m.model_names is not None:
                    if ps.model.name == m.model_names.default:
                        return ResolvedBackend(
                            m.backend_name,
                            self._model_name_args(m.model_names.resolved_default),
                        )

                    elif ps.model.name in m.model_names.alias_map:
                        return ResolvedBackend(
                            m.backend_name,
                            self._model_name_args(m.model_names.alias_map[ps.model.name]),
                        )

            else:
                raise NotImplementedError

        return None


##


class BackendStringBackendCatalog(BackendCatalog):
    def get_backend(self, service_cls: ta.Any, name: str, *args: ta.Any, **kwargs: ta.Any) -> ta.Any:
        ps = parse_backend_string(name)
        rv = ManifestBackendStringResolver(GlobalManifestLoader.load_values_of(BackendStringsManifest))
        rs = check.not_none(rv.resolve_backend_string(ps))

        return mc.registry_new(
            service_cls,
            rs.backend_name,
            *(rs.args or []),
            *args,
            **kwargs,
        )
