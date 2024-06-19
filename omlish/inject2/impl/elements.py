import typing as ta

from ... import lang
from ..elements import Element
from ..keys import Key
from .providers import ProviderImpl


class ElementCollection(lang.Final):
    def __init__(self, es: ta.Iterable[Element]) -> None:
        super().__init__()

        self._lst = list(es)

    @lang.cached_nullary
    def provider_map(self) -> ta.Mapping[Key, ProviderImpl]:
        raise NotImplementedError
