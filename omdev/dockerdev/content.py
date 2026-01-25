# ruff: noqa: UP007
import typing as ta

from omlish import dataclasses as dc
from omlish import lang


##


@dc.dataclass(frozen=True)
class Resource:
    path: str


def read_resource(r: Resource) -> str:
    d, _, f = r.path.rpartition('/')
    p = 'resources'
    if d:
        p = '.'.join([p, *d.split('/')])
    rs = lang.get_relative_resources(p, globals=globals())
    return rs[f].read_text()


#


StaticEnv: ta.TypeAlias = ta.Union[
    ta.Mapping[str, str | ta.Sequence[str]],
    ta.Callable[[], ta.Mapping[str, str | ta.Sequence[str]]],
]


@dc.dataclass(frozen=True)
class WithStaticEnv:
    body: 'Content'
    env: StaticEnv


#


@dc.dataclass(frozen=True)
class LazyContent:
    fn: ta.Callable[[], 'Content']


#


Content: ta.TypeAlias = ta.Union[
    str,
    Resource,
    WithStaticEnv,
    LazyContent,
    ta.Sequence['Content'],
]
