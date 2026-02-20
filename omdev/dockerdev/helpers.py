import io
import json
import tomllib
import typing as ta

from omlish import check
from omlish import lang

from .content import Content
from .content import Resource
from .content import StaticEnv
from .content import WithStaticEnv
from .content import read_resource
from .ops import Run
from .ops import Section
from .rendering import render_var_sections


##


def fragment_section(
        name: str,
        *,
        static_env: StaticEnv | None = None,
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


##


APT_CACHE_MOUNTS: ta.Sequence[str] = [
    '/var/lib/apt/lists',
    '/var/cache/apt',
]


def render_apt_install_dep_sets(*names: str) -> str:
    out = io.StringIO()

    dsl: list[tuple[str, ta.Sequence[str]]] = []

    for dsn in names:
        dso = tomllib.loads(read_resource(Resource(f'depsets/{dsn}.toml')))
        dsl.append((dsn, sorted(set(dso['deps']))))

    out.write(render_var_sections('DEPS', *dsl))
    out.write('\n')

    out.write('apt-get install -y $DEPS\n')

    return out.getvalue()


##


def read_versions_file_versions(
        resource_path: str,
        resource_name: str,
        keys: ta.Sequence[str],
) -> ta.Mapping[str, str]:
    check.not_isinstance(keys, str)
    rs = lang.get_relative_resources(resource_path, globals=globals())
    src = rs[resource_name].read_text()
    dct = json.loads(src)
    return {k: dct[k] for k in keys}
