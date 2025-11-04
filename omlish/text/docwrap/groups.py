import typing as ta

from ... import check
from ... import dataclasses as dc
from .parts import Blank
from .parts import Block
from .parts import Indent
from .parts import Part
from .parts import Text
from .parts import blockify


##


@dc.dataclass()
@dc.extra_class_params(default_repr_fn=dc.truthy_repr)
class _IndentGroup:
    n: int
    cs: list[ta.Union[Blank, Text, '_IndentGroup']] = dc.field(default_factory=list)


def group_indents(root: Part) -> Part:
    rg = _IndentGroup(0)
    stk: list[_IndentGroup] = [rg]

    for p in (root.ps if isinstance(root, Block) else [root]):
        if isinstance(p, Blank):
            stk[-1].cs.append(p)
            continue

        n: int
        t: Text
        if isinstance(p, Text):
            n, t = 0, p
        elif isinstance(p, Indent):
            n = p.n
            t = check.isinstance(p.p, Text)
        else:
            raise TypeError(p)

        while n < stk[-1].n:
            stk.pop()

        if n > stk[-1].n:
            nxt = _IndentGroup(n=n, cs=[t])
            stk[-1].cs.append(nxt)
            stk.append(nxt)

        else:
            check.state(stk[-1].n == n)
            stk[-1].cs.append(t)

    #

    def relativize(g: '_IndentGroup') -> None:
        for c in g.cs:
            if isinstance(c, _IndentGroup):
                check.state(c.n > g.n)
                relativize(c)
                c.n -= g.n

    relativize(rg)

    #

    def convert(g: '_IndentGroup') -> Part:
        if g.n < 1:
            check.state(g is rg)

        lst: list[Part] = []
        for c in g.cs:
            if isinstance(c, (Blank, Text)):
                lst.append(c)

            elif isinstance(c, _IndentGroup):
                lst.append(Indent(c.n, convert(c)))  # type: ignore[arg-type]

            else:
                raise TypeError(c)

        return blockify(*lst)

    return convert(rg)
