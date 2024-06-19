import typing as ta

from ... import check
from ... import lang
from ..bindings import Binding
from ..elements import Element
from ..elements import Elements
from ..exceptions import DuplicateKeyException
from ..keys import Key
from .providers import ProviderImpl
from .providers import make_provider_impl


class ElementCollection(lang.Final):
    def __init__(self, src: Elements) -> None:
        super().__init__()

        self._src = check.isinstance(src, Elements)
        self._es: ta.Sequence[Element] = list(src)

    @lang.cached_nullary
    def provider_map(self) -> ta.Mapping[Key, ProviderImpl]:
        pm: dict[Key, ProviderImpl] = {}
        for e in self._es:
            if isinstance(e, Binding):
                if e.key in pm:
                    raise DuplicateKeyException(e.key)
                p = make_provider_impl(e.provider)
                pm[e.key] = p
        return pm
