import typing as ta

from omcore import check
from omcore import dataclasses as dc
from omcore import lang


##


@ta.final
@dc.dataclass(frozen=True, kw_only=True)
@dc.extra_class_params(default_repr_fn=lang.opt_repr)
class Model:
    id: str
    name: str | None = ''

    backend: str

    provider: str | None = None
    base_url: str | None = None

    def __post_init__(self) -> None:
        check.non_empty_str(self.id)
        check.non_empty_str(self.backend)
