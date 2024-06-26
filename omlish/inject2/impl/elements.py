"""
Scopes in general:
 - clearly some notion of 'activeness for a given request'

Overrides + Scopes:
 -

Multi's + Scopes:
 - scope on a multi vs each element?
"""
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

    ##

    def _build_raw_binding_multimap(self, es: ta.Iterable[Element]) -> dict[Key, list[Binding]]:
        dct: dict[Key, list[Binding]] = {}
        for e in es:
            if isinstance(e, Binding):
                dct.setdefault(e.key, []).append(e)

            elif isinstance(e, Overrides):
                ovr = self._build_raw_binding_multimap(e.ovr)
                src = self._build_raw_binding_multimap(e.src)
                for k, b in src.items():
                    try:
                        bs = ovr[k]
                    except KeyError:
                        bs = src[k]
                    dct.setdefault(k, []).extend(bs)

        return dct

    def _make_binding_impl(self, b: Binding) -> BindingImpl:
        p = make_provider_impl(b.provider)
        return BindingImpl(b.key, p, b.scope, b)

    def _build_binding_map(self, es: ta.Iterable[Element]) -> dict[Key, BindingImpl]:
        pm: dict[Key, BindingImpl] = {}
        mm: dict[Key, list[BindingImpl]] = {}
        for k, bs in self._build_raw_binding_multimap(es).items():
            bis = [self._make_binding_impl(b) for b in bs]
            if k.multi:
                mm.setdefault(k, []).extend(bis)
            else:
                if len(bis) > 1:
                    raise DuplicateKeyException(k)
                [pm[k]] = bis
        if mm:
            for k, aps in mm.items():
                mp = MultiProviderImpl([ap.provider for ap in aps])
                pm[k] = BindingImpl(k, mp)  # FIXME: SCOPING
        return pm

    ##

    @lang.cached_function
    def binding_map(self) -> ta.Mapping[Key, BindingImpl]:
        return self._build_binding_map(self._es)
