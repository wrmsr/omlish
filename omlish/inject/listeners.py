import typing as ta

from .. import dataclasses as dc
from .. import lang
from .bindings import Binding
from .elements import Element
from .injector import Injector
from .keys import Key


##


ProvisionListener: ta.TypeAlias = ta.Callable[[
    Injector,
    Key,
    Binding,
    ta.Callable[[], ta.Any],
], ta.Callable[[], ta.Any]]


@dc.dataclass(frozen=True)
@dc.extra_params(cache_hash=True)
class ProvisionListenerBinding(Element, lang.Final):
    listener: ProvisionListener


def bind_provision_listener(l: ProvisionListener) -> Element:
    return ProvisionListenerBinding(l)
