# ruff: noqa: UP006 UP007
import typing as ta

from omlish.lite.inject import InjectorBindingOrBindings
from omlish.lite.inject import InjectorBindings
from omlish.lite.inject import inj

from ..cache import FileCache
from .cache import GithubFileCache


##


def bind_github(
        *,
        cache_dir: ta.Optional[str] = None,
) -> InjectorBindings:
    lst: ta.List[InjectorBindingOrBindings] = []

    if cache_dir is not None:
        lst.extend([
            inj.bind(GithubFileCache.Config(
                dir=cache_dir,
            )),
            inj.bind(GithubFileCache, singleton=True),
            inj.bind(FileCache, to_key=GithubFileCache),
        ])

    return inj.as_bindings(*lst)
