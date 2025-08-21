"""
TODO:
 - handle service_cls, like at all, lol
  - interop with registry somehow, probably? or is it strictly a different concern?
"""
import abc
import dataclasses as dc
import typing as ta

from omlish import lang
from omlish.manifests.globals import GlobalManifestLoader

from ...models.configs import ModelName
from ...models.configs import ModelPath
from ...models.configs import ModelRepo
from .manifests import BackendStringsManifest
from .parsing import ParsedBackendString


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


class CompositeBackendStringResolver(BackendStringResolver, lang.Abstract):  # noqa
    def __init__(
            self,
            children: ta.Iterable[BackendStringResolver],
    ) -> None:
        super().__init__()

        self._children = list(children)


class FirstCompositeBackendStringResolver(CompositeBackendStringResolver):
    def resolve_backend_string(self, ps: ParsedBackendString) -> ResolvedBackend | None:
        for c in self._children:
            if (r := c.resolve_backend_string(ps)) is not None:
                return r
        return None


@dc.dataclass()
class AmbiguousResolvedBackendStringError(Exception):
    ps: ParsedBackendString
    lst: list[tuple[BackendStringResolver, ResolvedBackend]]


class UniqueCompositeBackendStringResolver(CompositeBackendStringResolver):
    def resolve_backend_string(self, ps: ParsedBackendString) -> ResolvedBackend | None:
        lst: list[tuple[BackendStringResolver, ResolvedBackend]] = []
        for c in self._children:
            if (r := c.resolve_backend_string(ps)) is not None:
                lst.append((c, r))
        if not lst:
            return None
        elif len(lst) > 1:
            raise AmbiguousResolvedBackendStringError(ps, lst)
        else:
            return lst[0][1]


##


class ManifestBackendStringResolver(BackendStringResolver):
    def __init__(self, manifest: BackendStringsManifest) -> None:
        super().__init__()

        self._manifest = manifest

    def _resolve_name_model(
            self,
            ps: ParsedBackendString,
            mdl: ParsedBackendString.NameModel,
    ) -> ResolvedBackend | None:
        m = self._manifest
        if ps.backend is not None and ps.backend != m.backend_name:
            return None

        mn: str | None = mdl.name

        if mn == m.backend_name:
            if m.model_names is not None:
                mn = m.model_names.resolved_default
            else:
                mn = None

        else:
            if m.model_names is None:
                return None

            elif mdl.name == m.model_names.default:
                mn = m.model_names.resolved_default

            elif mdl.name in m.model_names.alias_map:
                mn = m.model_names.alias_map[mdl.name]

            elif ps.backend is None:
                return None

        return ResolvedBackend(
            m.backend_name,
            [ModelName(mn)] if mn is not None else [],
        )

    def _resolve_path_model(
            self,
            ps: ParsedBackendString,
            mdl: ParsedBackendString.PathModel,
    ) -> ResolvedBackend | None:
        if ps.backend is not None and ps.backend != self._manifest.backend_name:
            return None

        return ResolvedBackend(
            self._manifest.backend_name,
            [ModelPath(mdl.path)],
        )

    def _resolve_repo_model(
            self,
            ps: ParsedBackendString,
            mdl: ParsedBackendString.RepoModel,
    ) -> ResolvedBackend | None:
        if ps.backend is not None and ps.backend != self._manifest.backend_name:
            return None

        return ResolvedBackend(
            self._manifest.backend_name,
            [ModelRepo(
                namespace=mdl.namespace,
                repo=mdl.repo,
                tag=mdl.tag,
                path=mdl.path,
            )],
        )

    def resolve_backend_string(self, ps: ParsedBackendString) -> ResolvedBackend | None:
        mdl = ps.model
        if isinstance(mdl, ParsedBackendString.NameModel):
            return self._resolve_name_model(ps, mdl)
        elif isinstance(mdl, ParsedBackendString.PathModel):
            return self._resolve_path_model(ps, mdl)
        elif isinstance(mdl, ParsedBackendString.RepoModel):
            return self._resolve_repo_model(ps, mdl)
        else:
            raise TypeError(mdl)


##


def build_manifest_backend_string_resolver() -> BackendStringResolver:
    return UniqueCompositeBackendStringResolver([
        ManifestBackendStringResolver(m)
        for m in GlobalManifestLoader.load_values_of(BackendStringsManifest)
    ])
