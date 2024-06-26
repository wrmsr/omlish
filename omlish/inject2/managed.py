import contextlib
import typing as ta

from .eagers import eager
from .elements import Elements
from .elements import as_elements
from .injector import Injector
from .injector import create_injector
from .providers import as_provider


@contextlib.contextmanager
def create_managed_injector(es: Elements) -> ta.Generator[Injector]:
    i = create_injector(as_elements(
        bs,
        singleton(contextlib.ExitStack),
    ))
    with i[contextlib.ExitStack]:
        yield i
