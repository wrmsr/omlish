import typing as ta

from ... import check
from ... import lang
from ..bindings import Binding
from ..elements import Element
from ..elements import Elements
from ..exceptions import DuplicateKeyException
from ..keys import Key
from ..overrides import Overrides
from .bindings import BindingImpl
from .providers import MultiProviderImpl
from .providers import make_provider_impl


class ElementCollection(lang.Final):
    def __init__(self, src: Elements) -> None:
        super().__init__()

        self._src = check.isinstance(src, Elements)
        self._es: ta.Sequence[Element] = list(src)

    def _yield_element_bindings(self, e: Element) -> ta.Generator[BindingImpl, None, None]:
        if isinstance(e, Binding):
            p = make_provider_impl(e.provider)
            yield BindingImpl(e.key, p, e)

        elif isinstance(e, Overrides):
            ovr = self._build_provider_map(e.ovr)
            src = self._build_provider_map(e.src)
            for k, b in src.items():
                try:
                    yield ovr[k]
                except KeyError:
                    yield src[k]

        else:
            raise TypeError(e)

    def _build_provider_map(self, es: ta.Iterable[Element]) -> ta.Mapping[Key, BindingImpl]:
        pm: dict[Key, BindingImpl] = {}
        mm: dict[Key, list[BindingImpl]] = {}
        for e in es:
            for b in self._yield_element_bindings(e):
                if b.key.multi:
                    mm.setdefault(b.key, []).append(b)
                else:
                    if b.key in pm:
                        raise DuplicateKeyException(b.key)
                    pm[b.key] = b
        if mm:
            for k, aps in mm.items():
                mp = MultiProviderImpl([ap.provider for ap in aps])
                pm[k] = BindingImpl(k, mp)
        return pm

    @lang.cached_nullary
    def provider_map(self) -> ta.Mapping[Key, BindingImpl]:
        return self._build_provider_map(self._es)
