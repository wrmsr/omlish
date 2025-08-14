import dataclasses as dc
import typing as ta

from omlish import check

from ...models.names import ModelNameCollection


##


@dc.dataclass(frozen=True)
class ModelNameBackendStringPack:
    service_cls_names: ta.Sequence[str]
    backend_name: str
    model_names: ModelNameCollection

    def __post_init__(self) -> None:
        check.not_isinstance(self.service_cls_names, str)
