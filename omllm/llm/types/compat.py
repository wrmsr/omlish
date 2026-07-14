import typing as ta

from omcore import dataclasses as dc
from omcore import lang


##


@dc.dataclass(frozen=True, kw_only=True)
class Compat(lang.Abstract):
    pass


##


@ta.final
@dc.dataclass(frozen=True, kw_only=True)
class OpenaiCompat(Compat):
    max_tokens_field: str | None = None
