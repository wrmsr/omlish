import typing as ta

from omlish import check

from ... import minichain as mc
from ...minichain.backends.strings.parsing import parse_backend_string
from ...minichain.backends.strings.resolving import BackendStringResolver
from ...minichain.backends.strings.resolving import build_manifest_backend_string_resolver
from ...minichain.models.configs import ModelPath
from ...minichain.models.configs import ModelRepo
from .catalog import BackendCatalog


##


class BackendStringBackendCatalog(BackendCatalog):
    def __init__(
            self,
            resolver: BackendStringResolver | None = None,
    ) -> None:
        super().__init__()

        if resolver is None:
            resolver = build_manifest_backend_string_resolver()
        self._resolver = resolver

    def get_backend(self, service_cls: ta.Any, name: str, *args: ta.Any, **kwargs: ta.Any) -> ta.Any:
        ps = parse_backend_string(name)
        rs = check.not_none(self._resolver.resolve_backend_string(ps))

        al = list(rs.args or [])

        # FIXME: lol
        if al and isinstance(al[0], ModelRepo):
            [mr] = al
            from ...minichain.backends.impls.huggingface.repos import HuggingfaceModelRepoResolver
            mrr = HuggingfaceModelRepoResolver()
            mrp = check.not_none(mrr.resolve(mr))
            al = [ModelPath(mrp.path), *al[1:]]

        return mc.registry_new(
            service_cls,
            rs.backend_name,
            *al,
            *args,
            **kwargs,
        )
