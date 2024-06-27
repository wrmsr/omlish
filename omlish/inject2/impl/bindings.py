from ... import dataclasses as dc
from ... import lang
from ..bindings import Binding
from ..bindings import Scope
from ..bindings import Unscoped
from ..keys import Key
from .providers import ProviderImpl


##


@dc.dataclass(frozen=True, eq=False)
@dc.extra_params(cache_hash=True)
class BindingImpl(lang.Final):
    key: Key
    provider: ProviderImpl
    scope: Scope = Unscoped()
    binding: Binding | None = None
