import dataclasses as dc
import typing as ta

from omlish import check

from ...models.names import ModelNameCollection


##


@dc.dataclass(frozen=True)
class BackendStringsManifest:
    service_cls_names: ta.Sequence[str]
    backend_name: str

    _: dc.KW_ONLY

    model_names: ModelNameCollection | None = None

    def __post_init__(self) -> None:
        check.not_isinstance(self.service_cls_names, str)
