# ruff: noqa: UP006 UP007
import typing as ta

from omlish.lite.inject import InjectorBindingOrBindings
from omlish.lite.inject import InjectorBindings
from omlish.lite.inject import inj

from .cache import GithubFileCache


##


def bind_github() -> InjectorBindings:
    lst: ta.List[InjectorBindingOrBindings] = [
        inj.bind(GithubFileCache, singleton=True),
    ]

    return inj.as_bindings(*lst)
