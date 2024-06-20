from ... import dataclasses as dc
from ... import lang
from ..bindings import Binding
from ..keys import Key
from .providers import ProviderImpl


##


@dc.dataclass(frozen=True)
@dc.extra_params(cache_hash=True)
class BindingImpl(lang.Final):
    key: Key
    provider: ProviderImpl
    scope: Scope | None = None
    binding: Binding | None = None
