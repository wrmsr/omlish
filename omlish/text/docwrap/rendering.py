import functools
import io
import typing as ta

from ... import check
from .parts import Blank
from .parts import Block
from .parts import Indent
from .parts import List
from .parts import Part
from .parts import Text


##


@functools.lru_cache
def _indent_str(n: int) -> str:
    return ' ' * n


##


def render_to(root: Part, out: ta.Callable[[str], ta.Any]) -> None:
    i_stk: list[int] = [0]
    ci = 0

    def write(s: str, ti: int | None = None) -> None:
        if (nl := '\n' in s) and s != '\n':
            check.state(s[-1] == '\n')
            check.state(s.count('\n') == 1)

        if ti is None:
            ti = i_stk[-1]
        nonlocal ci
        if ci < ti:
            out(_indent_str(ti - ci))
            ci = ti

        out(s)

        if nl:
            ci = 0

    def rec(p: Part) -> None:
        nonlocal ci

        if isinstance(p, Blank):
            check.state(ci == 0)
            out('\n')

        elif isinstance(p, Text):
            write(p.s)
            write('\n')

        elif isinstance(p, Block):
            for c in p.ps:
                rec(c)

        elif isinstance(p, Indent):
            i_stk.append(i_stk[-1] + p.n)
            rec(p.p)
            i_stk.pop()

        elif isinstance(p, List):
            i_stk.append((li := i_stk[-1]) + len(p.d) + 1)
            sd = p.d + ' '
            for e in p.es:
                if isinstance(e, Blank):
                    rec(e)
                else:
                    check.state(ci == 0)
                    write(sd, li)
                    ci += len(sd)
                    rec(e)
            i_stk.pop()

        else:
            raise TypeError(p)

    rec(root)
    check.state(i_stk == [0])


def render(root: Part) -> str:
    buf = io.StringIO()
    render_to(root, buf.write)
    return buf.getvalue()


##


def dump_to(root: Part, out: ta.Callable[[str], ta.Any]) -> None:
    i = 0

    def write(s: str) -> None:
        out(_indent_str(i * 2))
        out(s)
        out('\n')

    def rec(p: Part) -> None:
        nonlocal i

        if isinstance(p, Blank):
            write('blank')

        elif isinstance(p, Text):
            write(f'text:{p.s!r}')

        elif isinstance(p, Block):
            write(f'block/{len(p.ps)}')
            i += 1
            for c in p.ps:
                rec(c)
            i -= 1

        elif isinstance(p, Indent):
            write(f'indent:{p.n}')
            i += 1
            rec(p.p)
            i -= 1

        elif isinstance(p, List):
            write(f'list/{len(p.es)}:{p.d!r}')
            i += 1
            for e in p.es:
                rec(e)
            i -= 1

        else:
            raise TypeError(p)

    rec(root)
    check.state(i == 0)


def dump(root: Part) -> str:
    buf = io.StringIO()
    dump_to(root, buf.write)
    return buf.getvalue()
