import typing as ta

from .content import Content
from .content import Resource
from .content import WithStaticEnv
from .ops import Run
from .ops import Section


##


def fragment_section(
        name: str,
        *,
        static_env: ta.Mapping[str, str | ta.Sequence[str]] | None = None,
        cache_mounts: ta.Sequence[str] | None = None,
) -> Section:
    body: Content = Resource(f'fragments/{name}.sh')

    if static_env is not None:
        body = WithStaticEnv(body, static_env)

    return Section(name, [
        Run(
            body,
            cache_mounts=cache_mounts or None,
        ),
    ])
