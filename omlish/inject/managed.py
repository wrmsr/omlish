"""
TODO:
 - proper ManagedProvider[Impl], DeferringProvider[Impl], closing (-> Deferring('close'))
"""
import contextlib
import typing as ta

from .binder import bind
from .elements import Elements
from .elements import as_elements
from .injector import Injector
from .injector import create_injector


@contextlib.contextmanager
def create_managed_injector(es: Elements) -> ta.Generator[Injector, None, None]:
    i = create_injector(as_elements(
        bind(contextlib.ExitStack, singleton=True, eager=True),
        es,
    ))
    with i[contextlib.ExitStack]:
        yield i
