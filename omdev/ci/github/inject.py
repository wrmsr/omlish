# ruff: noqa: UP006 UP007 UP045
import typing as ta

from omlish.lite.inject import InjectorBindingOrBindings
from omlish.lite.inject import InjectorBindings
from omlish.lite.inject import inj

from ..cache import DataCache
from ..cache import FileCache
from .cache import GithubCache


##


def bind_github() -> InjectorBindings:
    lst: ta.List[InjectorBindingOrBindings] = [
        inj.bind(GithubCache, singleton=True),
        inj.bind(DataCache, to_key=GithubCache),
        inj.bind(FileCache, to_key=GithubCache),
    ]

    return inj.as_bindings(*lst)
