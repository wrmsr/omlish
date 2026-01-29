"""
docker run --rm -it "$(docker build -q -f x/dockerdev/Dockerfile .)" bash
"""
import io
import typing as ta

from .content import LazyContent
from .content import Resource
from .helpers import APT_CACHE_MOUNTS
from .helpers import fragment_section
from .helpers import read_versions_file_versions
from .helpers import render_apt_install_deps
from .ops import Cmd
from .ops import Entrypoint
from .ops import Env
from .ops import From
from .ops import Op
from .ops import Run
from .ops import Section
from .ops import Workdir
from .ops import Write
from .rendering import render_op


##


BASE_IMAGE = 'ubuntu:24.04'

JDKS: ta.Sequence[str] = [
    'zulu21-ca-jdk',
    'zulu25-ca-jdk',
]

GO_VERSION = '1.25.6'
ZIG_VERSION = '0.15.2'

PYENV_VERSION_KEYS: ta.Sequence[str] = [
    '8',
    '13',
    '14',
]

CONFIG_FILES: ta.Sequence[str] = [
    '.gdbinit',
    '.tmux.conf',
    '.vimrc',
]

WORKDIR = '/omlish'


#


OPS: ta.Sequence[Op] = [
    From(BASE_IMAGE),

    # Section('timestamp', [
    #     Copy(src='docker/.timestamp', dst='/'),
    # ]),

    Section('locale', [
        Env([
            ('LANG', 'en_US.UTF-8'),
            ('LANGUAGE', 'en_US:en'),
            ('LC_ALL', 'en_US.UTF-8'),
        ]),
    ]),

    Section('deps', [
        Run(
            [
                Resource('fragments/apt.sh'),
                LazyContent(render_apt_install_deps),
            ],
            cache_mounts=APT_CACHE_MOUNTS,
        ),
    ]),

    fragment_section(
        'firefox',
        cache_mounts=APT_CACHE_MOUNTS,
    ),

    fragment_section(
        'docker',
        cache_mounts=APT_CACHE_MOUNTS,
    ),

    fragment_section(
        'jdk',
        static_env={'JDKS': JDKS},
        cache_mounts=APT_CACHE_MOUNTS,
    ),

    fragment_section('rustup'),

    fragment_section(
        'go',
        static_env={'GO_VERSION': GO_VERSION},
    ),

    fragment_section(
        'zig',
        static_env={'ZIG_VERSION': ZIG_VERSION},
    ),

    fragment_section('vcpkg'),

    fragment_section(
        'pyenv',
        static_env=lambda: {
            'PYENV_VERSIONS': list(read_versions_file_versions(*[
                f'PYTHON_{k}' for k in PYENV_VERSION_KEYS
            ]).values()),
        },
        cache_mounts=['/root/.pyenv_cache'],
    ),

    fragment_section('sshd'),

    # Section('x11', [
    #     Run('touch /root/.Xauthority'),
    #     Write('/root/xu', Resource('xu')),
    # ]),

    Section('configs', [
        Write(f'/root/{n}', Resource(f'configs/{n}'))
        for n in CONFIG_FILES
    ]),

    Section('entrypoint', [
        Workdir(WORKDIR),
        Entrypoint(['dumb-init', '--']),
        Cmd(['sh', '-c', 'echo "Ready" && sleep infinity']),
    ]),
]


##


def _main() -> None:
    out = io.StringIO()
    for i, section in enumerate(OPS):
        if i:
            out.write('\n\n\n')
        out.write(render_op(section))

    print(out.getvalue())


if __name__ == '__main__':
    _main()
