import contextlib
import typing as ta

from .. import dataclasses as dc
from .. import lang
from .bindings import as_binding
from .bindings import singleton
from .eagers import eager
from .elements import Elements
from .providers import fn
from .elements import as_elements
from .injector import Injector
from .injector import create_injector


@dc.dataclass(frozen=True)
@dc.extra_params(cache_hash=True)
class _JankManagedTag(lang.Final):
    tag: ta.Any


def jank_managed(a):
    b = as_binding(a)
    mg_key = dc.replace(b.key, tag=_JankManagedTag(b.key.tag))

    def prov(i: Injector):
        o = i[mg_key]
        i[contextlib.ExitStack].enter_context(o)
        return o

    return as_elements(
        dc.replace(b, key=mg_key),
        dc.replace(b, provider=fn(prov, b.key.cls)),
    )


@contextlib.contextmanager
def create_managed_injector(es: Elements) -> ta.Generator[Injector, None, None]:
    i = create_injector(as_elements(
        es,
        singleton(contextlib.ExitStack),
        eager(contextlib.ExitStack),
    ))
    with i[contextlib.ExitStack]:
        yield i
