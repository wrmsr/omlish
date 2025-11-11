import typing as ta

from omlish import check

from ...models.configs import ModelPath
from ...models.configs import ModelRepo
from ...models.repos.resolving import ModelRepoResolver
from ...registries.globals import get_registry_cls
from ..strings.parsing import parse_backend_string
from ..strings.resolving import BackendStringResolver
from ..strings.resolving import ResolveBackendStringArgs
from ..strings.resolving import build_manifest_backend_string_resolver
from .base import BackendCatalog


##


class BackendStringBackendCatalog(BackendCatalog):
    def __init__(
            self,
            string_resolver: BackendStringResolver | None = None,
            *,
            model_repo_resolver: ModelRepoResolver | None = None,
    ) -> None:
        super().__init__()

        if string_resolver is None:
            string_resolver = build_manifest_backend_string_resolver()
        self._string_resolver = string_resolver
        self._model_repo_resolver = model_repo_resolver

    def get_backend(self, service_cls: ta.Any, name: str, *args: ta.Any, **kwargs: ta.Any) -> BackendCatalog.Backend:
        ps = parse_backend_string(name)
        rs = check.not_none(self._string_resolver.resolve_backend_string(ResolveBackendStringArgs(
            service_cls,
            ps,
        )))

        al: list = list(rs.args or [])

        # FIXME: lol - move *into* local model classes as an injected dep?
        if al and isinstance(al[0], ModelRepo):
            [mr] = al
            mrr = check.not_none(self._model_repo_resolver)
            mrp = check.not_none(mrr.resolve(mr))
            al = [ModelPath(mrp.path), *al[1:]]

        cls = get_registry_cls(
            service_cls,
            rs.name,
        )

        return BackendCatalog.Backend(
            cls,
            al,
        )
