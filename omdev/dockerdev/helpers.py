import io
import tomllib
import typing as ta

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


def render_apt_install_deps() -> str:
    out = io.StringIO()

    dsl: list[tuple[str, ta.Sequence[str]]] = []

    for dsn in [
        'tools',
        'python',
    ]:
        dso = tomllib.loads(read_resource(Resource(f'depsets/{dsn}.toml')))
        dsl.append((dsn, sorted(set(dso['deps']))))

    out.write(render_var_sections('DEPS', *dsl))
    out.write('\n')

    out.write('apt-get install -y $DEPS\n')

    return out.getvalue()


##


def read_versions_file(file_path: str | None = None) -> ta.Mapping[str, str]:
    if file_path is None:
        file_path = '.versions'
    with open(file_path) as f:
        s = f.read()

    return {
        k.strip(): v.strip()
        for l in s.splitlines()
        for l in [l.split('#')[0].strip()]
        if '=' in l
        for k, _, v in [l.partition('=')]
    }


def read_versions_file_versions(*keys: str, file_path: str | None = None) -> ta.Mapping[str, str]:
    dct = read_versions_file(file_path)
    return {k: dct[k] for k in keys}
