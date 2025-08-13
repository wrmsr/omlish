import dataclasses as dc
import json
import typing as ta

from omlish import check

from ...standard import ModelNameCollection


##


@dc.dataclass(frozen=True)
class ModelNameBackendStringPack:
    service_cls: str | ta.Sequence[str]
    backend_name: str

    model_names: ModelNameCollection

    def __post_init__(self) -> None:
        check.equal((jd := dc.asdict(self)), json.loads(json.dumps(jd)))
