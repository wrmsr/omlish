"""
Scopes in general:
 - clearly some notion of 'activeness for a given request'

Overrides + Scopes:
 -

Multi's + Scopes:
 - scope on a multi vs each element?

Element Types:
 - Binding
 - Eager
 - Overrides
 - Expose
 - Private
 - ScopeSeed
"""
import typing as ta

from ... import check
from ... import collections as col
from ... import lang
from ..bindings import Binding
from ..eager import Eager
from ..elements import Element
from ..elements import Elements
from ..exceptions import DuplicateKeyException
from ..keys import Key
from ..overrides import Overrides
from ..private import Expose
from ..private import Private
from .bindings import BindingImpl
from .providers import MultiProviderImpl
from .providers import make_provider_impl


ElementT = ta.TypeVar('ElementT', bound=Element)


class ElementCollection(lang.Final):
    def __init__(self, es: Elements) -> None:
        super().__init__()

        self._es = check.isinstance(es, Elements)

        self._private_ecs: ta.MutableMapping[Private, ElementCollection] = col.IdentityKeyDict()

    @lang.cached_function
    def elements_of_type(self, *tys: type[ElementT]) -> ta.Sequence[ElementT]:
        return tuple(e for e in self._es if isinstance(e, tys))  # noqa

    def _get_private_element_collection(self, p: Private) -> 'ElementCollection':
        try:
            return self._private_ecs[p]
        except KeyError:
            self._private_ecs[p] = ec = ElementCollection(p.elements)
            return ec

    ##

    def _make_binding_impl(self, b: Binding) -> BindingImpl:
        p = make_provider_impl(b.provider)
        return BindingImpl(b.key, p, b.scope, b)

    ##

    def _build_raw_element_multimap(self, es: ta.Iterable[Element]) -> dict[Key, list[Element]]:
        dct: dict[Key, list[Element]] = {}
        for e in es:
            if isinstance(e, (Binding, Eager, Expose)):
                dct.setdefault(e.key, []).append(e)

            # elif isinstance(e, Private):
            #     raise NotImplementedError

            elif isinstance(e, Overrides):
                ovr = self._build_raw_element_multimap(e.ovr)
                src = self._build_raw_element_multimap(e.src)
                for k, b in src.items():
                    try:
                        bs = ovr[k]
                    except KeyError:
                        bs = src[k]
                    dct.setdefault(k, []).extend(bs)

        return dct

    @lang.cached_function
    def _raw_element_multimap(self) -> ta.Mapping[Key, ta.Sequence[Element]]:
        return self._build_raw_element_multimap(self._es)

    ##

    def _build_binding_map(self, bm: ta.Mapping[Key, ta.Sequence[Binding]]) -> dict[Key, BindingImpl]:
        pm: dict[Key, BindingImpl] = {}
        mm: dict[Key, list[BindingImpl]] = {}
        for k, bs in bm.items():
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

    @lang.cached_function
    def binding_map(self) -> ta.Mapping[Key, BindingImpl]:
        return self._build_binding_map(self._raw_element_multimap())
