"""
TODO:
 - proper ManagedProvider[Impl], DeferringProvider[Impl], closing (-> Deferring('close'))
"""
import contextlib
import typing as ta

from .eagers import eager
from .elements import Elements
from .elements import as_elements
from .injector import Injector
from .injector import create_injector
from .scopes import singleton


@contextlib.contextmanager
def create_managed_injector(es: Elements) -> ta.Generator[Injector, None, None]:
    i = create_injector(as_elements(
        es,
        singleton(contextlib.ExitStack),
        eager(contextlib.ExitStack),
    ))
    with i[contextlib.ExitStack]:
        yield i
