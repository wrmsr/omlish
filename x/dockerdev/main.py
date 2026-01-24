import io
import os.path
import tomllib
import typing as ta

from .content import Resource
from .content import read_resource
from .ops import Cmd
from .ops import Copy
from .ops import Entrypoint
from .ops import Env
from .ops import From
from .content import LazyContent
from .ops import Op
from .ops import Run
from .ops import Section
from .ops import Workdir
from .ops import Write
from .rendering import render_op
from .rendering import render_var_sections
from .templates import fragment_section


##


APT_CACHE_MOUNTS: ta.Sequence[str] = [
    '/var/lib/apt/lists',
    '/var/cache/apt',
]


##


BASE_IMAGE = 'ubuntu:24.04'

ZIG_VERSION = '0.15.2'
GO_VERSION = '1.25.6'

JDKS: ta.Sequence[str] = [
    'zulu21-ca-jdk',
    'zulu25-ca-jdk',
]

PYENV_VERSIONS: ta.Sequence[str] = [
    '3.8.20',
    '3.13.11',
    '3.14.2',
]

CONFIG_FILES: ta.Sequence[str] = [
    '.gdbinit',
    '.tmux.conf',
    '.vimrc',
]

WORKDIR = '/omlish'


#


def render_apt_install_deps() -> str:
    out = io.StringIO()

    dsl: list[tuple[str, ta.Sequence[str]]] = []

    for dsn in [
        'tools',
        'python',
    ]:
        dso = tomllib.loads(read_resource(Resource(f'depsets/{dsn}.toml')))
        dsl.append((dsn, dso['deps']))

    out.write(render_var_sections('DEPS', *dsl))
    out.write('\n')

    out.write('apt-get install -y $DEPS\n')

    return out.getvalue()


#


FROM = From(BASE_IMAGE)

TIMESTAMP = Section('timestamp', [
    Copy(src='docker/.timestamp', dst='/'),
])

LOCALE = Section('locale', [
    Env([
        ('LANG', 'en_US.UTF-8'),
        ('LANGUAGE', 'en_US:en'),
        ('LC_ALL', 'en_US.UTF-8'),
    ]),
])

APT = Section('deps', [
    Run([
        Resource('fragments/apt.sh'),
        LazyContent(render_apt_install_deps),
    ]),
])

FIREFOX = fragment_section(
    'firefox',
    cache_mounts=APT_CACHE_MOUNTS,
)

DOCKER = fragment_section(
    'docker',
    cache_mounts=APT_CACHE_MOUNTS,
)

JDK = fragment_section(
    'jdk',
    static_env={'JDKS': JDKS},
    cache_mounts=APT_CACHE_MOUNTS,
)

RUSTUP = fragment_section('rustup')

GO = fragment_section(
    'go',
    static_env={'GO_VERSION': GO_VERSION},
)

ZIG = fragment_section(
    'zig',
    static_env={'ZIG_VERSION': ZIG_VERSION},
)

VCPKG = fragment_section('vcpkg')

PYENV = fragment_section(
    'pyenv',
    static_env={'PYENV_VERSIONS': PYENV_VERSIONS},
    cache_mounts=['/root/.pyenv_cache'],
)

SSHD = fragment_section('sshd')

X11 = Section('x11', [
    Run('touch /root/.Xauthority'),
    Write('/root/xu', Resource('xu')),
])

CONFIGS = Section('configs', [
    Write(f'/root/{n}', Resource(f'configs/{n}'))
    for n in CONFIG_FILES
])

ENTRYPOINT = Section('entrypoint', [
    Workdir(WORKDIR),
    Entrypoint(['dumb-init', '--']),
    Cmd(['sh', '-c', 'echo "Ready" && sleep infinity']),
])


#


OPS: ta.Sequence[Op] = [
    FROM,

    TIMESTAMP,

    LOCALE,

    APT,

    FIREFOX,

    DOCKER,
    JDK,
    RUSTUP,
    GO,
    ZIG,
    VCPKG,

    PYENV,

    SSHD,

    X11,

    CONFIGS,

    ENTRYPOINT,
]


##


def _main() -> None:
    out = io.StringIO()
    for i, section in enumerate(OPS):
        if i:
            out.write('\n\n')
        out.write(render_op(section))
        out.write('\n')

    print(out.getvalue())

    with open(os.path.join(os.path.dirname(__file__), 'Dockerfile'), 'w') as f:
        f.write(out.getvalue())


if __name__ == '__main__':
    _main()
