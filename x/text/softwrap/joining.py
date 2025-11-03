"""
FIXME:
 - handle text not in blocks lol - `Indent(1, Text(...`, List('-', [Text(...`, etc
 - rename reflow or smth
"""
import typing as ta

from omlish import lang

from .parts import Blank
from .parts import Block
from .parts import Indent
from .parts import List
from .parts import Part
from .parts import Text
from .parts import blockify
from .utils import all_same


##


class TextJoiner(ta.Protocol):
    def __call__(self, strs: ta.Sequence[str], current_indent: int) -> ta.Sequence[str]: ...


def simple_text_joiner(strs: ta.Sequence[str], current_indent: int = 0) -> ta.Sequence[str]:
    return [' '.join(strs)]


def join_block_text(
        root: Part,
        text_joiner: TextJoiner = simple_text_joiner,
) -> Part:
    def rec(p: Part, ci: int) -> Part:
        if isinstance(p, (Blank, Text)):
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

        if not any(
                isinstance(ps[i], Text) and
                isinstance(ps[i + 1], Text)
                for i in range(len(ps) - 1)
        ):
            if not all_same(ps, p.ps):
                p = blockify(*ps)
            return p

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
            lambda x: map(Text, text_joiner(x, ci)) if isinstance(x, list) else [x],  # noqa
            new,
        ))

    return rec(root, 0)
