import uuid

from omcore import dataclasses as dc


##


@dc.dataclass(frozen=True, kw_only=True)
class StateConfig:
    new: bool = False

    chat_id: uuid.UUID | None = None
