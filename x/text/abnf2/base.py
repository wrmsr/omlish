"""
TODO:
 - cache lol
 - get greedier
 - match-powered optimizer
  - greedily compile regexes
 - mro-attr registry powered rule name dispatched visitor
  - also doable via a singledispatchmethod w/ Literal support
"""
import abc
import io
import itertools
import typing as ta

from omlish import check
from omlish import lang

from .errors import AbnfError


with lang.auto_proxy_import(globals()):
    from . import parsers


##


@ta.final
class Match(ta.NamedTuple):
    parser: 'Parser'
    start: int
    end: int
    children: tuple['Match', ...]

    @property
    def length(self) -> int:
        return self.end - self.start

    #

    # noinspection PyProtectedMember
    def __repr__(self) -> str:
        return (
            f'{self.__class__.__name__}('
            f'{self.parser._match_repr()}, '
            f'{self.start}, {self.end}'
            f'{f", {self.children!r}" if self.children else ""})'
        )

    def render_to(
            self,
            write: ta.Callable[[str], ta.Any],
            *,
            indent: int | None = None,
            _level: int = 0,
    ) -> None:
        ix: str | None = (' ' * (indent * _level)) if indent is not None else None
        if ix:
            write(ix)
        p = self.parser
        if isinstance(p, (parsers.StringLiteral, parsers.CaseInsensitiveStringLiteral)):
            write(f'literal<{self.start}-{self.end}>({p.value!r})')
        elif isinstance(p, parsers.RangeLiteral):
            write(f'literal<{self.start}-{self.end}>({p.value.lo!r}-{p.value.hi!r})')
        else:
            write(f'{p.__class__.__name__.lower()}<{self.start}-{self.end}>')
            if isinstance(p, parsers.Rule):
                write(f':{p.name}')
            if self.children:
                write('(')
                if ix is not None:
                    write('\n')
                for i, c in enumerate(self.children):
                    if i and ix is None:
                        write(', ')
                    c.render_to(write, indent=indent, _level=_level + 1)
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

    def map_children(self, fn: ta.Callable[['Match'], 'Match']) -> 'Match':
        return self._replace(children=tuple(map(fn, self.children)))

    def flat_map_children(self, fn: ta.Callable[['Match'], ta.Iterable['Match']]) -> 'Match':
        return self._replace(children=tuple(itertools.chain.from_iterable(map(fn, self.children))))


def longest_match(ms: ta.Iterable[Match]) -> Match | None:
    bm: Match | None = None
    bl = 0
    for m in ms:
        l = m.length
        if bm is None or l > bl:
            bm, bl = m, l
    return bm


##


class Parser(lang.Abstract, lang.Sealed):
    def _match_repr(self) -> str:
        return f'{self.__class__.__name__}@{id(self)}'

    @abc.abstractmethod
    def _iter_parse(self, ctx: '_Context', start: int) -> ta.Iterator[Match]:
        raise NotImplementedError


##


class Grammar(lang.Final):
    @ta.final
    class _Rule:
        def __init__(self, name: str, parser: Parser) -> None:
            self.name = check.non_empty_str(name)
            self.name_f = name.casefold()
            self.parser = check.isinstance(parser, Parser)

    def __init__(
            self,
            *rules: ta.Mapping[str, Parser] | ta.Iterable[tuple[str, Parser]],
            root: str | None = None,
    ) -> None:
        super().__init__()

        rules_by_name: dict[str, Grammar._Rule] = {}
        rules_by_name_f: dict[str, Grammar._Rule] = {}
        rules_by_parser: dict[Parser, Grammar._Rule] = {}
        for rs in rules:
            if isinstance(rs, ta.Mapping):
                rts: ta.Iterable[tuple[str, Parser]] = rs.items()
            else:
                rts = rs
            for n, p in rts:
                gr = Grammar._Rule(n, p)
                check.not_in(gr.name, rules_by_name)
                check.not_in(gr.name_f, rules_by_name_f)
                check.not_in(gr.parser, rules_by_parser)
                rules_by_name[n] = gr
                rules_by_name_f[gr.name_f] = gr
                rules_by_parser[gr.parser] = gr
        self._rules_by_name: ta.Mapping[str, Grammar._Rule] = rules_by_name
        self._rules_by_name_f: ta.Mapping[str, Grammar._Rule] = rules_by_name_f
        self._rules_by_parser: ta.Mapping[Parser, Grammar._Rule] = rules_by_parser

        self._root = root
        self._root_f = root.casefold() if root is not None else None
        if self._root_f is not None:
            check.not_none(self._root_f)

    @property
    def root(self) -> str | None:
        return self._root

    def rule(self, name: str) -> Parser | None:
        try:
            gr = self._rules_by_name_f[name.casefold()]
        except KeyError:
            return None
        return gr.parser

    def iter_parse(
            self,
            source: str,
            root: str | None = None,
            *,
            start: int = 0,
    ) -> ta.Iterator[Match]:
        if root is None:
            if (root := self._root) is None:
                raise AbnfError('No root or default root specified')

        rule = check.not_none(self.rule(root))  # noqa
        ctx = _Context(self, source)
        return ctx.iter_parse(rule, start)

    def parse(
            self,
            source: str,
            root: str | None = None,
            *,
            start: int = 0,
    ) -> Match | None:
        return longest_match(self.iter_parse(
            source,
            root,
            start=start,
        ))


##


class _Context(lang.Final):
    def __init__(self, grammar: Grammar, source: str) -> None:
        super().__init__()

        self._grammar = grammar
        self._source = source

    @property
    def grammar(self) -> Grammar:
        return self._grammar

    @property
    def source(self) -> str:
        return self._source

    # noinspection PyProtectedMember
    def iter_parse(self, parser: Parser, start: int) -> ta.Iterator[Match]:
        return parser._iter_parse(self, start)


##


def iter_parse(
        obj: Grammar | Parser,
        src: str,
        *,
        root: str | None = None,
        start: int = 0,
) -> ta.Iterator[Match]:
    if isinstance(obj, Grammar):
        gram = obj
    elif isinstance(obj, Parser):
        if root is None:
            root = 'root'
        gram = Grammar({root: obj}, root=root)
    else:
        raise TypeError(obj)

    return gram.iter_parse(
        src,
        root,
        start=start,
    )


def parse(
        obj: Grammar | Parser,
        src: str,
        *,
        root: str | None = None,
        start: int = 0,
) -> Match | None:
    return longest_match(iter_parse(
        obj,
        src,
        root=root,
        start=start,
    ))
