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

if ta.TYPE_CHECKING:
    from . import private as private_
else:
    private_ = lang.proxy_import('.private', __package__)


ElementT = ta.TypeVar('ElementT', bound=Element)


class ElementCollection(lang.Final):
    def __init__(self, es: Elements) -> None:
        super().__init__()

        self._es = check.isinstance(es, Elements)

        self._private_infos: ta.MutableMapping[Private, 'private_.PrivateInfo'] | None = None

    ##

    def _get_private_info(self, p: Private) -> 'private_.PrivateInfo':
        if (pis := self._private_infos) is None:
            self._private_infos = pis = col.IdentityKeyDict()
        try:
            return pis[p]
        except KeyError:
            pis[p] = ec = private_.PrivateInfo(self, p)
            return ec

    ##

    def _build_raw_element_multimap(self, es: ta.Iterable[Element]) -> dict[Key, list[Element]]:
        dct: dict[Key, list[Element]] = {}

        def add(k: Key, *e: Element) -> None:
            dct.setdefault(k, []).extend(e)

        for e in es:
            if isinstance(e, (Binding, Eager, Expose)):
                add(e.key, e)

            elif isinstance(e, Private):
                pi = self._get_private_info(e)
                for k, ips in pi.internal_providers().items():
                    add(k, *ips)

            elif isinstance(e, Overrides):
                ovr = self._build_raw_element_multimap(e.ovr)
                src = self._build_raw_element_multimap(e.src)
                for k, b in src.items():
                    try:
                        bs = ovr[k]
                    except KeyError:
                        bs = src[k]
                    add(k, *bs)

            else:
                raise TypeError(e)

        return dct

    @lang.cached_function
    def element_multimap(self) -> ta.Mapping[Key, ta.Sequence[Element]]:
        return self._build_raw_element_multimap(self._es)

    @lang.cached_function
    def elements_of_type(self, *tys: type[ElementT]) -> ta.Sequence[ElementT]:
        return tuple(e for es in self.element_multimap().values() for e in es if isinstance(e, tys))  # noqa

    ##

    def _make_binding_impls(self, e: Element) -> ta.Iterable[BindingImpl]:
        if isinstance(e, Binding):
            p = make_provider_impl(e.provider)
            return (BindingImpl(e.key, p, e.scope, e),)

        elif isinstance(e, private_.InternalProvider):
            raise NotImplementedError

        elif isinstance(e, Eager):
            return ()

        else:
            raise TypeError(e)

    def _build_binding_impl_map(self, em: ta.Mapping[Key, ta.Sequence[Element]]) -> dict[Key, BindingImpl]:
        pm: dict[Key, BindingImpl] = {}
        mm: dict[Key, list[BindingImpl]] = {}
        for k, es in em.items():
            bis = [bi for e in es for bi in self._make_binding_impls(e)]
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
    def binding_impl_map(self) -> ta.Mapping[Key, BindingImpl]:
        return self._build_binding_impl_map(self.element_multimap())
