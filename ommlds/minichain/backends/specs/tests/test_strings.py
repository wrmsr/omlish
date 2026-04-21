import typing as ta

from omlish import check
from omlish import collections as col
from omlish import dataclasses as dc
from omlish.manifests.globals import GlobalManifestLoader

from ....chat.choices.services import ChatChoicesService
from ....configs import Config
from ....models.configs import ModelName
from ....registries.globals import get_global_registry
from ...strings.manifests import BackendStringsManifest
from ..types import BackendSpec
from ..types import ModelBackendSpec
from ..types import NameBackendSpec


##


@dc.dataclass(frozen=True)
class ResolvedBackendSpec:
    service_cls: ta.Any
    spec: BackendSpec

    cls: ta.Any
    configs: ta.Sequence[Config] | None = None
    children: ta.Sequence[ResolvedBackendSpec] | None = None


def resolve_backend_spec(service_cls: ta.Any, spec: BackendSpec) -> ResolvedBackendSpec:
    rt = get_global_registry().get_registered_type(service_cls)

    if isinstance(spec, NameBackendSpec):
        cls = rt.lookup(spec.name)

        configs: list[Config] | None = None

        if spec.configs:
            if all(isinstance(c, Config) for c in spec.configs):
                configs = spec.configs  # type: ignore[assignment]  # noqa

            else:
                raise NotImplementedError

        return ResolvedBackendSpec(
            service_cls,
            spec,

            cls,
            configs,
        )

    elif isinstance(spec, ModelBackendSpec):
        alias_map = col.multi_map(
            (an, bsm)
            for bsm in GlobalManifestLoader.load_values_of(BackendStringsManifest)
            if rt.name in bsm.service_cls_names
            if (mnc := bsm.model_names) is not None
            for an in mnc.resolved
        )

        bsm = check.single(alias_map[spec.name])

        return resolve_backend_spec(
            service_cls,
            NameBackendSpec(
                bsm.backend_name,
                (
                    *(spec.configs or ()),
                    ModelName(spec.name),
                ),
            ),
        )

    else:
        raise TypeError(spec)


##


def test_strings():
    print(resolve_backend_spec(ChatChoicesService, NameBackendSpec('openai')))
    print(resolve_backend_spec(ChatChoicesService, ModelBackendSpec('gpt')))
