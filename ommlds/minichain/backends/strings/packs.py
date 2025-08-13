import dataclasses as dc
import typing as ta

from ...standard import ModelNameCollection


##


@dc.dataclass(frozen=True)
class ModelNameBackendStringPack:
    service_cls: str | ta.Sequence[str]
    backend_name: str

    model_names: ModelNameCollection
