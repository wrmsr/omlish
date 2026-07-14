import typing as ta

from omcore import check
from omcore import dataclasses as dc
from omcore import lang


##


@ta.final
@dc.dataclass(frozen=True)
@dc.extra_class_params(terse_repr=True, cache_hash=True)
class ModelKey:
    provider: str
    id: str

    def __post_init__(self) -> None:
        check.non_empty_str(self.provider)
        check.non_empty_str(self.id)


@ta.final
@dc.dataclass(frozen=True, kw_only=True)
@dc.extra_class_params(default_repr_fn=lang.opt_repr)
class Model:
    key: ModelKey

    name: str | None = ''

    backend: str

    base_url: str | None = None
