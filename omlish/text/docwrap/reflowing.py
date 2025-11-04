"""
FIXME:
 - use wrapping.py with all its todos
"""
import dataclasses as dc
import textwrap
import typing as ta

from ... import lang
from ..textwrap import TextwrapOpts
from .parts import Blank
from .parts import Block
from .parts import Indent
from .parts import List
from .parts import Part
from .parts import Text
from .parts import blockify
from .utils import all_same


##


class TextReflower(ta.Protocol):
    def __call__(self, strs: ta.Sequence[str], current_indent: int) -> ta.Sequence[str]: ...


class NopReflower:
    def __call__(self, strs: ta.Sequence[str], current_indent: int = 0) -> ta.Sequence[str]:
        return strs


@dc.dataclass(frozen=True)
class JoiningReflower:
    sep: str = ' '

    def __call__(self, strs: ta.Sequence[str], current_indent: int = 0) -> ta.Sequence[str]:
        return [self.sep.join(strs)]


@dc.dataclass(frozen=True)
class TextwrapReflower:
    sep: str = ' '
    opts: TextwrapOpts = TextwrapOpts()

    def __call__(self, strs: ta.Sequence[str], current_indent: int = 0) -> ta.Sequence[str]:
        return textwrap.wrap(
            self.sep.join(strs),
            **dc.asdict(dc.replace(
                self.opts,
                width=self.opts.width - current_indent,
            )),
        )


##


def reflow_block_text(
        root: Part,
        reflower: TextReflower = JoiningReflower(),
) -> Part:
    def rec(p: Part, ci: int) -> Part:
        if isinstance(p, Blank):
            return p

        elif isinstance(p, Text):
            if (rf := reflower([p.s], ci)) != [p.s]:
                p = blockify(*map(Text, rf))  # noqa
            return p

        elif isinstance(p, Indent):
            if (np := rec(p.p, ci + p.n)) is not p.p:
                p = Indent(p.n, np)  # type: ignore[arg-type]
            return p

        elif isinstance(p, List):
            ne = [rec(e, ci + len(p.d) + 1) for e in p.es]
            if not all_same(ne, p.es):
                p = List(p.d, ne)
            return p

        elif not isinstance(p, Block):
            raise TypeError(p)

        ps = [rec(c, ci) for c in p.ps]

        new: list[Part | list[str]] = []
        for c in ps:
            if isinstance(c, Text):
                if new and isinstance(x := new[-1], list):
                    x.append(c.s)
                else:
                    new.append([c.s])
            else:
                new.append(c)

        return blockify(*lang.flatmap(
            lambda x: map(Text, reflower(x, ci)) if isinstance(x, list) else [x],  # noqa
            new,
        ))

    return rec(root, 0)
