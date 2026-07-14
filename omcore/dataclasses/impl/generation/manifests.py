import dataclasses as dc
import json

from .plans import Plans


##


@dc.dataclass(frozen=True)
class DataclassTransformManifest:
    qualname: str
    digest: str
    plans: Plans

    def to_json(self) -> str:
        return json.dumps(
            dc.asdict(self),  # noqa
            indent=2,
        )
