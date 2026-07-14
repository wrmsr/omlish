import typing as ta

from omcore import dataclasses as dc
from omcore import lang


##


class StableDataclass(lang.Abstract):
    def replace(self, **kwargs: ta.Any) -> ta.Self:
        return dc.replace_is_not(self, **kwargs)
