import typing as ta

from omlish import dataclasses as dc
from omlish import lang


##


class StableDataclass(lang.Abstract):
    def replace(self, **kwargs: ta.Any) -> ta.Self:
        return dc.replace_is_not(self, **kwargs)
