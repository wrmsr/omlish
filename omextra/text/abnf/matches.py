import io
import itertools
import typing as ta

from omlish import lang

from .internal import Regex
from .ops import CaseInsensitiveStringLiteral
from .ops import Op
from .ops import RangeLiteral
from .ops import RuleRef
from .ops import StringLiteral


##


@ta.final
class Match(ta.NamedTuple):
    op: 'Op'
    start: int
    end: int
    children: tuple['Match', ...]

    @property
    def length(self) -> int:
        return self.end - self.start

    #

    def __repr__(self) -> str:
        return (
            f'{self.__class__.__name__}('
            f'{self.op._match_repr()}, '  # noqa
            f'{self.start}, {self.end}'
            f'{f", {self.children!r}" if self.children else ""})'
        )

    def render_to(
            self,
            write: ta.Callable[[str], ta.Any],
            *,
            indent: int | None = None,
            _depth: int = 0,
    ) -> None:
        ix: str | None = (' ' * (indent * _depth)) if indent is not None else None
        if ix:
            write(ix)

        o = self.op

        if isinstance(o, (StringLiteral, CaseInsensitiveStringLiteral)):
            write(f'literal<{self.start}-{self.end}>({o.value!r})')

        elif isinstance(o, RangeLiteral):
            write(f'literal<{self.start}-{self.end}>({o.value.lo!r}-{o.value.hi!r})')

        elif isinstance(o, Regex):
            write(f'regex<{self.start}-{self.end}>({o.pat.pattern!r})')

        else:
            write(f'{o.__class__.__name__.lower()}<{self.start}-{self.end}>')

            if isinstance(o, RuleRef):
                write(f':{o.name}')

            if self.children:
                write('(')
                if ix is not None:
                    write('\n')

                for i, c in enumerate(self.children):
                    if i and ix is None:
                        write(', ')

                    c.render_to(write, indent=indent, _depth=_depth + 1)

                    if ix is not None:
                        write(',\n')

                if ix:
                    write(ix)

                write(')')

    def render(
            self,
            *,
            indent: int | None = None,
    ) -> str:
        sb = io.StringIO()
        self.render_to(sb.write, indent=indent)
        return sb.getvalue()

    def __str__(self) -> str:
        return self.render()

    #

    def replace_children(self, *children: 'Match') -> 'Match':
        if lang.seqs_identical(children, self.children):
            return self

        return self._replace(children=children)

    def map_children(self, fn: ta.Callable[['Match'], 'Match']) -> 'Match':
        return self.replace_children(*map(fn, self.children))

    def flat_map_children(self, fn: ta.Callable[['Match'], ta.Iterable['Match']]) -> 'Match':
        return self.replace_children(*itertools.chain.from_iterable(map(fn, self.children)))


##


def longest_match(ms: ta.Iterable[Match]) -> Match | None:
    bm: Match | None = None
    bl = 0
    for m in ms:
        l = m.length
        if bm is None or l > bl:
            bm, bl = m, l
    return bm


def filter_matches(
        fn: ta.Callable[[Match], bool],
        m: Match,
        *,
        keep_children: bool = False,
) -> Match:
    def inner(x: Match) -> ta.Iterable[Match]:
        if fn(x):
            return (rec(x),)

        elif keep_children:
            return lang.flatten(inner(c) for c in x.children)

        else:
            return ()

    def rec(c: Match) -> Match:
        return c.flat_map_children(inner)

    return rec(m)
