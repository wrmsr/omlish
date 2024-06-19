import typing as ta

from ... import check
from ... import lang
from ..elements import Element
from ..elements import Elements
from ..keys import Key
from .providers import ProviderImpl


class ElementCollection(lang.Final):
    def __init__(self, es: Elements) -> None:
        super().__init__()

        self._es = check.isinstance(es, Elements)
        self._lst: ta.Sequence[Element] = list(es)

    @lang.cached_nullary
    def provider_map(self) -> ta.Mapping[Key, ProviderImpl]:
        raise NotImplementedError
