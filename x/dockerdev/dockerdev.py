import typing as ta

from omlish import dataclasses as dc
from omlish import lang


##


class Op(lang.Abstract):
    pass


@dc.dataclass(frozen=True, kw_only=True)
class Copy(Op):
    src: str
    dst: str


@dc.dataclass(frozen=True)
class Env(Op):
    key: str
    value: str


@dc.dataclass(frozen=True)
class Run(Op):
    body: str

    _: dc.KW_ONLY

    cache_mounts: ta.Sequence[str] | None = None


"""
FROM ubuntu:24.04
Copy(src='docker/.timestamp', dst='/')


## locale

Env('LANG', 'en_US.UTF-8')
Env('LANGUAGE', 'en_US:en')
Env('LC_ALL', 'en_US.UTF-8')


## deps

RUN \
    --mount=target=/var/lib/apt/lists,type=cache,sharing=locked \
    --mount=target=/var/cache/apt,type=cache,sharing=locked \
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
        x11-apps \
]



## firefox

RUN \
    --mount=target=/var/lib/apt/lists,type=cache,sharing=locked \
    --mount=target=/var/cache/apt,type=cache,sharing=locked \
( \
    {firefox.sh}
)


## docker

RUN \
    --mount=target=/var/lib/apt/lists,type=cache,sharing=locked \
    --mount=target=/var/cache/apt,type=cache,sharing=locked \
( \
    {docker.sh}
)


## jdk

RUN \
    --mount=target=/var/lib/apt/lists,type=cache,sharing=locked \
    --mount=target=/var/cache/apt,type=cache,sharing=locked \
( \
    {jdk.sh}
)


## rustup

RUN ( \
    {rustup.sh}
)


## go

RUN ( \
    {go.sh}
)


## zig

RUN ( \
    {zig.sh}
)


## vcpkg

RUN ( \
    {vcpkg.sh}
)


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

RUN ( \
    {sshd.sh}
)


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
