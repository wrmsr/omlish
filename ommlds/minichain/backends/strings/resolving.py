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
from ...registries.globals import get_global_registry
from .manifests import BackendStringsManifest
from .parsing import ParsedBackendString


##


@dc.dataclass(frozen=True)
class ResolveBackendStringArgs:
    service_cls: ta.Any
    parsed: ParsedBackendString


@dc.dataclass(frozen=True)
class ResolveBackendStringResult:
    service_cls: ta.Any
    name: str

    _: dc.KW_ONLY

    args: ta.Sequence[ta.Any] | None = None


@dc.dataclass()
class AmbiguousBackendStringResolutionError(Exception):
    ra: ResolveBackendStringArgs
    lst: list[tuple['BackendStringResolver', ResolveBackendStringResult]]


class BackendStringResolver(lang.Abstract):
    @abc.abstractmethod
    def resolve_backend_string(self, args: ResolveBackendStringArgs) -> ResolveBackendStringResult | None:
        raise NotImplementedError


##


class CompositeBackendStringResolver(BackendStringResolver, lang.Abstract):
    def __init__(
            self,
            children: ta.Iterable[BackendStringResolver],
    ) -> None:
        super().__init__()

        self._children = list(children)


class FirstCompositeBackendStringResolver(CompositeBackendStringResolver):
    def resolve_backend_string(self, args: ResolveBackendStringArgs) -> ResolveBackendStringResult | None:
        for c in self._children:
            if (r := c.resolve_backend_string(args)) is not None:
                return r
        return None


class UniqueCompositeBackendStringResolver(CompositeBackendStringResolver):
    def resolve_backend_string(self, args: ResolveBackendStringArgs) -> ResolveBackendStringResult | None:
        lst: list[tuple[BackendStringResolver, ResolveBackendStringResult]] = []
        for c in self._children:
            if (r := c.resolve_backend_string(args)) is not None:
                lst.append((c, r))
        if not lst:
            return None
        elif len(lst) > 1:
            raise AmbiguousBackendStringResolutionError(args, lst)
        else:
            return lst[0][1]


##


class ManifestBackendStringResolver(BackendStringResolver):
    def __init__(self, manifest: BackendStringsManifest) -> None:
        super().__init__()

        self._manifest = manifest
        self._service_cls_set = {
            get_global_registry().get_registry_type_cls(scn)
            for scn in manifest.service_cls_names
        }

    def _resolve_name_model(
            self,
            args: ResolveBackendStringArgs,
            mdl: ParsedBackendString.NameModel,
    ) -> ResolveBackendStringResult | None:
        m = self._manifest
        if args.parsed.backend is not None and args.parsed.backend != m.backend_name:
            return None

        mn: str | None = mdl.name

        if args.parsed.backend == m.backend_name and mn is not None:
            pass

        elif mn == m.backend_name:
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

            elif args.parsed.backend is None:
                return None

        return ResolveBackendStringResult(
            args.service_cls,
            m.backend_name,
            args=[ModelName(mn)] if mn is not None else None,
        )

    def _resolve_path_model(
            self,
            args: ResolveBackendStringArgs,
            mdl: ParsedBackendString.PathModel,
    ) -> ResolveBackendStringResult | None:
        if args.parsed.backend is not None and args.parsed.backend != self._manifest.backend_name:
            return None

        return ResolveBackendStringResult(
            args.service_cls,
            self._manifest.backend_name,
            args=[ModelPath(mdl.path)],
        )

    def _resolve_repo_model(
            self,
            args: ResolveBackendStringArgs,
            mdl: ParsedBackendString.RepoModel,
    ) -> ResolveBackendStringResult | None:
        if args.parsed.backend is not None and args.parsed.backend != self._manifest.backend_name:
            return None

        return ResolveBackendStringResult(
            args.service_cls,
            self._manifest.backend_name,
            args=[ModelRepo(
                namespace=mdl.namespace,
                repo=mdl.repo,
                tag=mdl.tag,
                path=mdl.path,
            )],
        )

    def resolve_backend_string(self, args: ResolveBackendStringArgs) -> ResolveBackendStringResult | None:
        if args.service_cls not in self._service_cls_set:
            return None

        mdl = args.parsed.model
        if isinstance(mdl, ParsedBackendString.NameModel):
            return self._resolve_name_model(args, mdl)
        elif isinstance(mdl, ParsedBackendString.PathModel):
            return self._resolve_path_model(args, mdl)
        elif isinstance(mdl, ParsedBackendString.RepoModel):
            return self._resolve_repo_model(args, mdl)
        else:
            raise TypeError(mdl)


##


def build_manifest_backend_string_resolver() -> BackendStringResolver:
    return UniqueCompositeBackendStringResolver([
        ManifestBackendStringResolver(m)
        for m in GlobalManifestLoader.load_values_of(BackendStringsManifest)
    ])
