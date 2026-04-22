import inspect
import typing as ta

from omlish import check
from omlish import collections as col
from omlish import dataclasses as dc
from omlish import dispatch
from omlish import lang
from omlish import marshal as msh
from omlish import reflect as rfl
from omlish.manifests.globals import GlobalManifestLoader

from ....chat.choices.services import ChatChoicesService
from ....configs import Config
from ....models.configs import ModelName
from ....registries.globals import get_global_registry
from ....registries.registry import Registry
from ...strings.manifests import BackendStringsManifest
from ..types import BackendSpec
from ..types import ModelBackendSpec
from ..types import NameBackendSpec


##


@dc.dataclass(frozen=True)
@dc.extra_class_params(default_repr_fn=lang.opt_repr)
class ResolvedBackendSpec:
    service_cls: ta.Any
    spec: BackendSpec

    cls: ta.Any
    configs: ta.Sequence[Config] | None = None
    children: ta.Sequence[ResolvedBackendSpec] | None = None


class BackendSpecResolver:
    def __init__(
            self,
            *,
            registry: Registry | None = None,
    ) -> None:
        super().__init__()

        if registry is None:
            registry = get_global_registry()
        self._registry = check.not_none(registry)

    @lang.cached_function
    def _inspect_cls_config_arg(self, cls: ta.Any) -> rfl.Type:
        sig = inspect.signature(cls)  # noqa
        cfgs_arg = next(iter(sig.parameters.values()))
        check.state(cfgs_arg.kind == inspect.Parameter.VAR_POSITIONAL)
        check.is_not(cfgs_arg.annotation, inspect.Parameter.empty)
        check.is_not(cfgs_arg.annotation, Config)
        return rfl.type_(cfgs_arg.annotation)

    class _ForService:
        def __init__(
                self,
                o: BackendSpecResolver,
                service_cls: ta.Any,
        ) -> None:
            super().__init__()

            self._o = o
            self._service_cls = service_cls

            self._rt = o._registry.get_registered_type(service_cls)

        @dispatch.method()
        def resolve(self, spec: BackendSpec) -> ResolvedBackendSpec:
            raise TypeError(spec)

        @resolve.register
        def resolve_name(self, spec: NameBackendSpec) -> ResolvedBackendSpec:
            cls = self._rt.lookup(spec.name)

            configs: list[Config] | None = None

            if spec.configs:
                if all(isinstance(c, Config) for c in spec.configs):
                    configs = spec.configs  # type: ignore[assignment]  # noqa

                else:
                    cfg_rty = self._o._inspect_cls_config_arg(cls)  # noqa

                    configs = []
                    for c in spec.configs:
                        if not isinstance(c, Config):
                            c = msh.unmarshal(c, cfg_rty)

                        configs.append(c)

            return ResolvedBackendSpec(
                self._service_cls,
                spec,

                cls,
                configs,
            )

        @lang.cached_function
        def _model_alias_map(self) -> ta.Mapping[str, ta.Sequence[BackendStringsManifest]]:
            return col.multi_map(
                (an, bsm)
                for bsm in GlobalManifestLoader.load_values_of(BackendStringsManifest)
                if self._rt.name in bsm.service_cls_names
                if (mnc := bsm.model_names) is not None
                for an in mnc.resolved
            )

        @resolve.register
        def resolve_model(self, spec: ModelBackendSpec) -> ResolvedBackendSpec:
            bsm = check.single(self._model_alias_map()[spec.name])

            return self.resolve(
                NameBackendSpec(
                    bsm.backend_name,
                    (
                        *(spec.configs or ()),
                        ModelName(spec.name),
                    ),
                ),
            )

    @lang.cached_function
    def _for_service(self, service_cls: ta.Any) -> _ForService:
        return self._ForService(self, service_cls)

    def resolve(self, service_cls: ta.Any, spec: BackendSpec) -> ResolvedBackendSpec:
        return self._for_service(service_cls).resolve(spec)


##


def test_strings():
    bsr = BackendSpecResolver()

    for _ in range(2):
        print(bsr.resolve(ChatChoicesService, NameBackendSpec('openai')))
        print(bsr.resolve(ChatChoicesService, ModelBackendSpec('gpt', [{'api_key': 'foo'}])))
