import collections.abc
import functools
import io
import json
import shlex
import typing as ta

from omlish import check

from .content import Content
from .content import LazyContent
from .content import Resource
from .content import WithStaticEnv
from .content import read_resource
from .ops import Cmd
from .ops import Copy
from .ops import Entrypoint
from .ops import Env
from .ops import From
from .ops import Op
from .ops import Run
from .ops import Section
from .ops import Workdir
from .ops import Write


##


INDENT = ' ' * 2


##
# Content


@functools.singledispatch
def render_content(c: Content) -> str:
    raise TypeError(c)


@render_content.register(str)
def render_str(c: str) -> str:
    return c


@render_content.register(Resource)
def render_resource(c: Resource) -> str:
    return read_resource(c)


@render_content.register(WithStaticEnv)
def render_with_static_env(c: WithStaticEnv) -> str:
    out = io.StringIO()

    if c.env:
        kvs = c.env

        if callable(kvs):
            kvs = kvs()

        for k, v in kvs.items():
            if isinstance(v, str):
                pass
            elif isinstance(v, ta.Sequence):
                v = ' '.join(v)
            else:
                raise TypeError(v)

            out.write(f'export {k}={sh_quote(v)} ;\\\n')

        out.write('\\\n')

    out.write(render_content(c.body))

    return out.getvalue()


@render_content.register(LazyContent)
def render_lazy_content(c: LazyContent) -> str:
    return render_content(c.fn())


@render_content.register(collections.abc.Sequence)
def render_sequence_content(c: ta.Sequence[Content]) -> str:
    return '\n'.join([render_content(cc) for cc in c])


##
# Misc


def sh_quote(s: str) -> str:
    if not s:
        return "''"

    s = shlex.quote(s)

    if not s.startswith("'"):
        check.not_in("'", s)
        s = f"'{s}'"

    return s


def render_cmd_parts(*parts: str) -> str:
    out = io.StringIO()

    out.write('[ \\\n')
    for i, p in enumerate(parts):
        out.write(INDENT)
        out.write(json.dumps(p))
        if i < len(parts) - 1:
            out.write(',')
        out.write(' \\\n')

    out.write(']')

    return out.getvalue()


def render_var_sections(
        name: str,
        *dep_sections: tuple[str, ta.Sequence[str]],
) -> str:
    out = io.StringIO()

    out.write(f'{name}="" ;\n\n')

    for i, (n, ds) in enumerate(dep_sections):
        if i:
            out.write('\n')

        out.write(f'# {n}\n\n')

        out.write(f'{name}="${name}\n')
        for d in ds:
            out.write(f'{INDENT}{d}\n')
        out.write('" ;\n')

    return out.getvalue()


##
# Ops


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


@render_op.register(Write)
def render_write(op: Write) -> str:
    out = io.StringIO()

    out.write("RUN echo '\\\n")

    c = render_content(op.content)
    s = sh_quote(c)[1:-1]
    for l in s.splitlines(keepends=True):
        # l = l.replace('$', '\\$')
        if l.endswith('\n'):
            out.write(l[:-1])
            out.write('\\n\\\n')
        else:
            out.write(l)
            out.write('\\\n')

    out.write(f"' {'>>' if op.append else '>'} {op.path}")

    return out.getvalue()


@render_op.register(Run)
def render_run(op: Run) -> str:
    out = io.StringIO()

    if op.cache_mounts:
        out.write('RUN \\\n')
        for cm in op.cache_mounts:
            out.write(INDENT + f'--mount=target={cm},type=cache,sharing=locked \\\n')
        out.write('( \\\n')
    else:
        out.write('RUN (\\\n')

    s = render_content(op.body)
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
    return f'ENTRYPOINT {render_cmd_parts(*op.parts)}'


@render_op.register(Cmd)
def render_cmd(op: Cmd) -> str:
    return f'CMD {render_cmd_parts(*op.parts)}'
