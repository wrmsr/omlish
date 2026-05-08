import collections.abc
import functools
import io
import json
import re
import shlex
import typing as ta

from omlish import check
from omlish import dataclasses as dc

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
from .ops import Shell
from .ops import User
from .ops import Workdir
from .ops import Write


##


INDENT = ' ' * 2


##
# Context


@dc.dataclass(frozen=True, kw_only=True)
class RenderContext:
    resource_preambles: ta.Sequence[tuple[re.Pattern, ta.Sequence[str]]] | None = None

    write_chmod: str | None = None


##
# Content


@functools.singledispatch
def render_content(c: Content, ctx: RenderContext) -> str:
    raise TypeError(c)


@render_content.register(str)
def render_str(c: str, ctx: RenderContext) -> str:
    return c


@render_content.register(Resource)
def render_resource(c: Resource, ctx: RenderContext) -> str:
    s = read_resource(c)

    for pat, lines in ctx.resource_preambles or []:
        if lines and pat.match(c.path):
            s = '\n'.join([*lines, '', s])

    return s


@render_content.register(WithStaticEnv)
def render_with_static_env(c: WithStaticEnv, ctx: RenderContext) -> str:
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

    out.write(render_content(c.body, ctx))

    return out.getvalue()


@render_content.register(LazyContent)
def render_lazy_content(c: LazyContent, ctx: RenderContext) -> str:
    return render_content(c.fn(), ctx)


@render_content.register(collections.abc.Sequence)
def render_sequence_content(c: ta.Sequence[Content], ctx: RenderContext) -> str:
    return '\n'.join([render_content(cc, ctx) for cc in c])


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
def render_op(op: Op, ctx: RenderContext) -> str:
    raise TypeError(op)


@render_op.register(From)
def render_from(op: From, ctx: RenderContext) -> str:
    return f'FROM {op.spec}'


@render_op.register(Section)
def render_section(op: Section, ctx: RenderContext) -> str:
    out = io.StringIO()

    out.write(f'## {op.header or ""}'.strip())
    out.write('\n')

    for i, c in enumerate(op.body):
        if i:
            out.write('\n')
        out.write('\n')
        out.write(render_op(c, ctx))

    return out.getvalue()


@render_op.register(Env)
def render_env(op: Env, ctx: RenderContext) -> str:
    return '\n'.join([
        f'ENV {k}={v}'
        for k, v in op.items
    ])


@render_op.register(User)
def render_user(op: User, ctx: RenderContext) -> str:
    return f'USER {op.user}'


@render_op.register(Shell)
def render_shell(op: Shell, ctx: RenderContext) -> str:
    return f'SHELL {render_cmd_parts(*op.parts)}'


@render_op.register(Copy)
def render_copy(op: Copy, ctx: RenderContext) -> str:
    return f'COPY {op.src} {op.dst}'


@render_op.register(Write)
def render_write(op: Write, ctx: RenderContext) -> str:
    out = io.StringIO()

    c = render_content(op.content, ctx)

    eof = 'EOF'
    ei = 0
    while eof in c:
        eof = f'EOF{ei}'
        ei += 1

    out.write(f"RUN cat {'>>' if op.append else '>'} {op.path} <<'{eof}'")
    if ctx.write_chmod is not None:
        out.write(f' && chmod {ctx.write_chmod} {op.path}')

    out.write('\n')
    out.write(c.strip())
    out.write('\n')
    out.write(eof)
    out.write('\n')

    return out.getvalue()


@render_op.register(Run)
def render_run(op: Run, ctx: RenderContext) -> str:
    out = io.StringIO()

    if op.cache_mounts:
        out.write('RUN \\\n')
        for cm in op.cache_mounts:
            out.write(INDENT + ''.join([
                '--mount=',
                ','.join([
                    f'target={cm}',
                    'type=cache',
                    'sharing=locked',
                    *(op.cache_mount_args or []),
                ]),
                ' \\\n',
            ]))
        out.write('( \\\n')
    else:
        out.write('RUN (\\\n')

    s = render_content(op.body, ctx)
    for l in s.strip().splitlines():
        out.write(l)
        if not l.rstrip().endswith('\\'):
            out.write('\\')
        out.write('\n')

    out.write(')')

    return out.getvalue()


@render_op.register(Workdir)
def render_workdir(op: Workdir, ctx: RenderContext) -> str:
    return f'WORKDIR {op.path}'


@render_op.register(Entrypoint)
def render_entrypoint(op: Entrypoint, ctx: RenderContext) -> str:
    return f'ENTRYPOINT {render_cmd_parts(*op.parts)}'


@render_op.register(Cmd)
def render_cmd(op: Cmd, ctx: RenderContext) -> str:
    return f'CMD {render_cmd_parts(*op.parts)}'
