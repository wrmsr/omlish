import typing as ta

from omcore import check
from omcore import dataclasses as dc
from omcore import lang

from .compat import Compat
from .options import Options


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

    #

    compat: Compat | None = None

    #

    @ta.final
    @dc.dataclass(frozen=True, kw_only=True)
    @dc.extra_class_params(default_repr_fn=lang.opt_repr)
    class Http:
        base_url: str | None = None

        extra_headers: ta.Mapping[str, str] | None = None

    http: Http | None = None

    #

    default_options: Options | None = None
