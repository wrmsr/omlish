"""
Scopes in general:
 - clearly some notion of 'activeness for a given request'

Overrides + Scopes:
 -

Multi's + Scopes:
 - scope on a multi vs each element?

Element Types:
 - Binding
 - ProvisionListenerBinding
 - SetBinding
 - MapBinding
 - Eager
 - Overrides
 - Expose
 - Private
 - ScopeBinding
"""
import copy
import typing as ta

from ... import check
from ... import collections as col
from ... import lang
from ..bindings import Binding
from ..eagers import Eager
from ..elements import Element
from ..elements import Elements
from ..exceptions import ConflictingKeyError
from ..exceptions import UnboundKeyError
from ..keys import Key
from ..listeners import ProvisionListenerBinding
from ..multis import MapBinding
from ..multis import MapProvider
from ..multis import SetBinding
from ..multis import SetProvider
from ..overrides import Overrides
from ..privates import Expose
from ..privates import Private
from ..scopes import ScopeBinding
from ..types import Scope
from .bindings import BindingImpl
from .multis import make_multi_provider_impl
from .origins import Origins
from .origins import set_origins
from .providers import ProviderImpl
from .providers import make_provider_impl
from .scopes import make_scope_impl


if ta.TYPE_CHECKING:
    from . import privates as privates_
else:
    privates_ = lang.proxy_import('.privates', __package__)


ElementT = ta.TypeVar('ElementT', bound=Element)


class ElementCollection(lang.Final):
    def __init__(self, es: Elements) -> None:
        super().__init__()

        self._es = check.isinstance(es, Elements)

        self._private_infos: ta.MutableMapping[Private, privates_.PrivateInfo] | None = None

    ##

    def _get_private_info(self, p: Private) -> 'privates_.PrivateInfo':
        if (pis := self._private_infos) is None:
            self._private_infos = pis = col.IdentityKeyDict()
        try:
            return pis[p]
        except KeyError:
            pis[p] = ec = privates_.PrivateInfo(self, p)
            return ec

    ##

    def _build_raw_element_multimap(
            self,
            es: ta.Iterable[Element],
            out: dict[Key | None, list[Element]] | None = None,
    ) -> dict[Key | None, list[Element]]:
        if out is None:
            out = {}

        def add(k: Key | None, *e: Element) -> None:
            out.setdefault(k, []).extend(e)

        for e in es:
            if isinstance(e, ScopeBinding):
                add(None, e)
                sci = make_scope_impl(e.scope)
                if (sae := sci.auto_elements()) is not None:
                    self._build_raw_element_multimap(sae, out)

            elif isinstance(e, (Binding, Eager, Expose)):
                add(e.key, e)

            elif isinstance(e, Private):
                pi = self._get_private_info(e)
                self._build_raw_element_multimap(pi.owner_elements(), out)

            elif isinstance(e, (SetBinding, MapBinding)):
                add(e.multi_key, e)

            elif isinstance(e, ProvisionListenerBinding):
                add(None, e)

            elif isinstance(e, Overrides):
                ovr = self._build_raw_element_multimap(e.ovr)
                src = self._build_raw_element_multimap(e.src)
                for k, b in src.items():  # FIXME: merge None keys?
                    try:
                        bs = ovr[k]
                    except KeyError:
                        bs = b
                    add(k, *bs)

            else:
                raise TypeError(e)

        return out

    @lang.cached_function
    def element_multimap(self) -> ta.Mapping[Key | None, ta.Sequence[Element]]:
        return self._build_raw_element_multimap(self._es)

    @lang.cached_function
    def elements_of_type(self, *tys: type[ElementT]) -> ta.Sequence[ElementT]:
        return tuple(e for es in self.element_multimap().values() for e in es if isinstance(e, tys))  # noqa

    ##

    def _get_single_binding(self, k: Key, bs: ta.Sequence[Binding]) -> Binding:
        if not bs:
            raise UnboundKeyError(k)

        elif len(bs) > 1:
            d: dict = {}
            for b in bs:
                d.setdefault(b, []).append(b)
            if len(d) > 1:
                raise ConflictingKeyError(k)
            l = check.single(d.values())
            b = copy.copy(l[0])
            set_origins(b, Origins(tuple(o for c in l for o in c.origins)))
            return b

        else:
            return check.isinstance(check.single(bs), Binding)

    def _build_binding_impl_map(self, em: ta.Mapping[Key | None, ta.Sequence[Element]]) -> dict[Key, BindingImpl]:
        pm: dict[Key, BindingImpl] = {}
        for k, es in em.items():
            if k is None:
                continue

            es_by_ty = col.multi_map_by(type, es)

            es_by_ty.pop(Eager, None)
            es_by_ty.pop(Expose, None)
            es_by_ty.pop(ProvisionListenerBinding, None)

            if (bs := es_by_ty.pop(Binding, None)):
                b = self._get_single_binding(k, bs)  # type: ignore

                p: ProviderImpl
                if isinstance(b.provider, (SetProvider, MapProvider)):
                    p = make_multi_provider_impl(b.provider, es_by_ty)

                else:
                    p = make_provider_impl(b.provider)

                pm[k] = BindingImpl(b.key, p, b.scope, b)

            if es_by_ty:
                raise TypeError(set(es_by_ty))

        return pm

    @lang.cached_function
    def binding_impl_map(self) -> ta.Mapping[Key, BindingImpl]:
        return self._build_binding_impl_map(self.element_multimap())

    ##

    @lang.cached_function
    def eager_keys_by_scope(self) -> ta.Mapping[Scope, ta.Sequence[Key]]:
        bim = self.binding_impl_map()
        ret: dict[Scope, list[Key]] = {}
        for e in self.elements_of_type(Eager):
            bi = bim[e.key]
            ret.setdefault(bi.scope, []).append(e.key)
        return ret
