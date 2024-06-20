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


ElementT = ta.TypeVar('ElementT', bound=Element)


class ElementCollection(lang.Final):
    def __init__(self, es: Elements) -> None:
        super().__init__()

        self._es = check.isinstance(es, Elements)

    @lang.cached_function
    def elements_of_type(self, *tys: type[ElementT]) -> ta.Sequence[ElementT]:
        return tuple(e for e in self._es if isinstance(e, tys))  # noqa

    def _yield_element_bindings(self, e: Element) -> ta.Generator[BindingImpl, None, None]:
        if isinstance(e, Binding):
            p = make_provider_impl(e.provider)
            yield BindingImpl(e.key, p, e.scope, e)

        elif isinstance(e, Overrides):
            ovr = self._build_binding_map(e.ovr)
            src = self._build_binding_map(e.src)
            for k, b in src.items():
                try:
                    yield ovr[k]
                except KeyError:
                    yield src[k]

    def _build_binding_map(self, es: ta.Iterable[Element]) -> ta.Mapping[Key, BindingImpl]:
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

    @lang.cached_function
    def binding_map(self) -> ta.Mapping[Key, BindingImpl]:
        return self._build_binding_map(self._es)
