import typing as ta

from omlish import dataclasses as dc
from omlish import lang


##


@dc.dataclass(frozen=True)
class Resource:
    path: str


@dc.dataclass(frozen=True)
class WithStaticEnv:
    body: 'Content'
    env: ta.Mapping[str, str | ta.Sequence[str]]


Content: ta.TypeAlias = ta.Union[
    str,
    Resource,
    WithStaticEnv,
    ta.Sequence['Content'],
]


##


def read_resource(r: Resource) -> str:
    d, _, f = r.path.rpartition('/')
    p = 'resources'
    if d:
        p = '.'.join([p, *d.split('/')])
    rs = lang.get_relative_resources(p, globals=globals())
    return rs[f].read_text()
