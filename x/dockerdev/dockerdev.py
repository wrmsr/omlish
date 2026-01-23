import functools
import typing as ta

from omlish import dataclasses as dc
from omlish import lang


##


class Op(lang.Abstract):
    pass


@dc.dataclass(frozen=True)
class Section(Op):
    header: str
    body: ta.Sequence[Op]


@dc.dataclass(frozen=True, kw_only=True)
class Copy(Op):
    src: str
    dst: str


@dc.dataclass(frozen=True)
class Env(Op):
    items: ta.Iterable[tuple[str, str]]


@dc.dataclass(frozen=True)
class Run(Op):
    @dc.dataclass(frozen=True)
    class Resource:
        path: str

    body: str | Resource

    _: dc.KW_ONLY

    cache_mounts: ta.Sequence[str] | None = None


##


@functools.singledispatch
def render_op(op: Op) -> str:
    raise TypeError(op)


@render_op.register(Section)
def render_section(op: Section) -> str:
    raise TypeError(op)


@render_op.register(Copy)
def render_copy(op: Copy) -> str:
    raise TypeError(op)


@render_op.register(Copy)
def render_env(op: Env) -> str:
    raise TypeError(op)


@render_op.register(Run)
def render_run(op: Run) -> str:
    raise TypeError(op)


##


APT_CACHE_MOUNTS: ta.Sequence[str] = [
    '/var/lib/apt/lists',
    '/var/cache/apt',
]


def fragment_section(
        name: str,
        *,
        apt_cache: bool = False,
) -> Section:
    return Section(name, [
        Run(
            Run.Resource(f'fragments/{name}.sh'),
            cache_mounts=APT_CACHE_MOUNTS if apt_cache else None,
        ),
    ])


##


"""
FROM ubuntu:24.04

Copy(src='docker/.timestamp', dst='/')
"""


LOCALE = Section('locale', [
    Env([
        ('LANG', 'en_US.UTF-8'),
        ('LANGUAGE', 'en_US:en'),
        ('LC_ALL', 'en_US.UTF-8'),
    ]),
])


"""
## deps

apt_cache=True:

( \
    rm -f /etc/apt/apt.conf.d/docker-clean && \
\
    export DEBIAN_FRONTEND=noninteractive && \
    apt-get update && \
\
    apt-get install -y locales && \
    locale-gen en_US.UTF-8 && \
\
    apt-get upgrade -y && \
    apt-get install -y apt-utils && \
\
    apt-get install -y \
\
    ...
"""


TOOL_PACKAGES = [
        'apt-transport-https',
        'aria2',
        'bison',
        'bmon',
        'btop',
        'build-essential',
        'ca-certificates',
        'clang',
        'cmake',
        'curl',
        'cvs',
        'dnsutils',
        'dumb-init',
        'emacs',
        'file',
        'flex',
        'g++',
        'g++-14',
        'gcc',
        'gcc-14',
        'gdb',
        'git',
        'gnupg',
        'gnupg-agent',
        'graphviz',
        'htop',
        'iputils-ping',
        'iputils-tracepath',
        'irssi',
        'jq',
        'less',
        'libdb-dev',
        'libpq-dev',
        'llvm',
        'lsb-release',
        'lsof',
        'make',
        'man-db',
        'mercurial',
        'moreutils',
        'mosh',
        'nano',
        'ncdu',
        'net-tools',
        'netcat-openbsd',
        'nodejs',
        'npm',
        'openssh-server',
        'perl',
        'pkg-config',
        'postgresql-client',
        'protobuf-compiler',
        'ripgrep',
        'ruby',
        'silversearcher-ag',
        'socat',
        'software-properties-common',
        'strace',
        'subversion',
        'sudo',
        'tcpdump',
        'telnet',
        'tmux',
        'unzip',
        'vim',
        'wget',
        'xsltproc ',
        'zip',
        'zsh',
]

PYTHON_BUILD_PACKAGES = [
        'build-essential',
        'gdb',
        'lcov',
        'libbz2-dev',
        'libffi-dev',
        'libgdbm-compat-dev',
        'libgdbm-dev',
        'liblzma-dev',
        'libncurses5-dev',
        'libreadline6-dev',
        'libsqlite3-dev',
        'libssl-dev',
        'lzma',
        'lzma-dev',
        'pkg-config',
        'tk-dev',
        'uuid-dev',
        'zlib1g-dev',
]

X11_PACKAGES = [
        'x11-apps',
]


FIREFOX = fragment_section('firefox', apt_cache=True)
DOCKER = fragment_section('docker', apt_cache=True)
JDK = fragment_section('jdk', apt_cache=True)
RUSTUP = fragment_section('rustup')
GO = fragment_section('go')
ZIG = fragment_section('zig')
VCPKG = fragment_section('vcpkg')


"""


## versions

COPY .versions /root/


## python

RUN \
    --mount=target=/root/.pyenv_cache,type=cache,sharing=locked \
( \
    git clone 'https://github.com/pyenv/pyenv' /root/.pyenv && \
    grep '^PYTHON_' /root/.versions | while read L ; do \
        K=$(echo "$L" | cut -d= -f1 | cut -d_ -f2-) && \
        case $K in \
            8|13|14) true ;; \
            *) continue ;; \
        esac && \
        echo "Installing Python $K" && \
        V=$(echo "$L" | cut -d= -f2) && \
        PYTHON_BUILD_CACHE_PATH=/root/.pyenv_cache /root/.pyenv/bin/pyenv install -s "$V" ; \
    done \
)


## config files

COPY \
\
    docker/dev/.gdbinit \
    docker/dev/.tmux.conf \
    docker/dev/.vimrc \
\
    /root/


## sshd
"""


SSHD = fragment_section('sshd')


"""
## x

RUN touch /root/.Xauthority

COPY \
\
    docker/dev/xu \
\
    /root/


## entrypoint

WORKDIR /omlish

ENTRYPOINT ["dumb-init", "--"]
CMD ["sh", "-c", "echo 'Ready' && sleep infinity"]
"""


SECTIONS: ta.Sequence[Section] = [
    LOCALE,
    FIREFOX,
    DOCKER,
    JDK,
    RUSTUP,
    GO,
    ZIG,
    VCPKG,
]


##


def _main() -> None:
    pass


if __name__ == '__main__':
    _main()
