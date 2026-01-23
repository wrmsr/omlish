"""
TODO:
 - GO_VERSION / ZIG_VERSION
 - .versions file?
"""
import functools
import io
import tomllib
import typing as ta

from omlish import dataclasses as dc
from omlish import lang


##


@dc.dataclass(frozen=True)
class Resource:
    path: str


def read_resource(r: Resource) -> str:
    d, _, f = r.path.rpartition('/')
    p = '.'.join(['resources', *d.split('/')])
    rs = lang.get_relative_resources(p, globals=globals())
    return rs[f].read_text()


##


class Op(lang.Abstract):
    pass


@dc.dataclass(frozen=True)
class From(Op):
    spec: str


@dc.dataclass(frozen=True)
class Section(Op):
    header: str | None
    body: ta.Sequence[Op]


@dc.dataclass(frozen=True)
class Env(Op):
    items: ta.Iterable[tuple[str, str]]


@dc.dataclass(frozen=True, kw_only=True)
class Copy(Op):
    src: str
    dst: str


RunBody: ta.TypeAlias = str | Resource | ta.Sequence[str | Resource]


@dc.dataclass(frozen=True)
class Run(Op):
    body: RunBody

    _: dc.KW_ONLY

    cache_mounts: ta.Sequence[str] | None = None


@dc.dataclass(frozen=True)
class Workdir(Op):
    path: str


@dc.dataclass(frozen=True)
class Entrypoint(Op):
    parts: ta.Sequence[str]


@dc.dataclass(frozen=True)
class Cmd(Op):
    parts: ta.Sequence[str]


##


@functools.singledispatch
def render_op(op: Op) -> str:
    raise TypeError(op)


@render_op.register(From)
def render_from(op: From) -> str:
    return f'FROM {op.spec}'


@render_op.register(Section)
def render_section(op: Section) -> str:
    out = io.StringIO()
    out.write(f'## {op.header or ""}'.strip())
    out.write('\n')
    for i, c in enumerate(op.body):
        if i:
            out.write('\n')
        out.write('\n')
        out.write(render_op(c))
    return out.getvalue()


@render_op.register(Env)
def render_env(op: Env) -> str:
    return '\n'.join([
        f'ENV {k}={v}'
        for k, v in op.items
    ])


@render_op.register(Copy)
def render_copy(op: Copy) -> str:
    return f'COPY {op.src} {op.dst}'


def get_run_body(body: RunBody) -> str:
    if isinstance(body, str):
        return body

    elif isinstance(body, Resource):
        return read_resource(body)

    elif isinstance(body, ta.Sequence):
        raise NotImplementedError

    else:
        raise TypeError(body)


@render_op.register(Run)
def render_run(op: Run) -> str:
    s = get_run_body(op.body)

    out = io.StringIO()

    if op.cache_mounts:
        out.write('RUN \\\n')
        for cm in op.cache_mounts:
            out.write(f'    --mount=target={cm},type=cache,sharing=locked \\\n')
        out.write(') \\\n')
    else:
        out.write('RUN (\\\n')

    for l in s.strip().splitlines():
        out.write(l)
        if not l.rstrip().endswith('\\'):
            out.write('\\')
        out.write('\n')
    out.write(')')
    return out.getvalue()


@render_op.register(Workdir)
def render_workdir(op: Workdir) -> str:
    return f'WORKDIR {op.path}'


@render_op.register(Entrypoint)
def render_entrypoint(op: Entrypoint) -> str:
    return f'ENTRYPOINT {op.parts!r}'  # FIXME: lol


@render_op.register(Cmd)
def render_cmd(op: Cmd) -> str:
    return f'CMD {op.parts!r}'  # FIXME: lol


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
            Resource(f'fragments/{name}.sh'),
            cache_mounts=APT_CACHE_MOUNTS if apt_cache else None,
        ),
    ])


##


FROM = From('ubuntu:24.04')

# COPY_TIMESTAMP = Copy(src='docker/.timestamp', dst='/')

LOCALE = Section('locale', [
    Env([
        ('LANG', 'en_US.UTF-8'),
        ('LANGUAGE', 'en_US:en'),
        ('LC_ALL', 'en_US.UTF-8'),
    ]),
])


# DEPS = Section('deps', [
#
# ])
# apt-get install -y \


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


"""


ENTRYPOINT = Section('entrypoint', [
    Workdir('/omlish'),
    Entrypoint(['dumb-init', '--']),
    Cmd(['sh', '-c', "echo 'Ready' && sleep infinity"]),
])


SECTIONS: ta.Sequence[Section] = [
    FROM,

    LOCALE,

    FIREFOX,

    DOCKER,
    JDK,
    RUSTUP,
    GO,
    ZIG,
    VCPKG,

    SSHD,

    ENTRYPOINT,
]


##


def _main() -> None:
    pds = tomllib.loads(read_resource(Resource('depsets/python.toml')))
    pds_deps = pds['deps']
    print(pds_deps)

    for section in SECTIONS:
        print(render_op(section))
        print('\n')


if __name__ == '__main__':
    _main()
