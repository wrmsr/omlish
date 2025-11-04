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

    def __repr__(self) -> str:
        return (
            f'{self.__class__.__name__}('
            f'{self.parser._match_repr()}, '  # noqa
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
            if isinstance(p, parsers.RuleRef):
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


class Parser(lang.Abstract, lang.PackageSealed):
    def _match_repr(self) -> str:
        return f'{self.__class__.__name__}@{id(self)}'

    @abc.abstractmethod
    def _iter_parse(self, ctx: '_Context', start: int) -> ta.Iterator[Match]:
        raise NotImplementedError


##


class Rule(lang.Final):
    def __init__(
            self,
            name: str,
            parser: Parser,
            *,
            insignificant: bool = False,
    ) -> None:
        super().__init__()

        self._name = check.non_empty_str(name)
        self._name_f = name.casefold()
        self._parser = check.isinstance(parser, Parser)
        self._insignificant = insignificant

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self._name!r})'

    @property
    def name(self) -> str:
        return self._name

    @property
    def name_f(self) -> str:
        return self._name_f

    @property
    def parser(self) -> Parser:
        return self._parser

    @property
    def insignificant(self) -> bool:
        return self._insignificant


class Grammar(lang.Final):
    def __init__(
            self,
            *rules: Rule,
            root: Rule | str | None = None,
    ) -> None:
        super().__init__()

        rules_set: set[Rule] = set()
        rules_by_name: dict[str, Rule] = {}
        rules_by_name_f: dict[str, Rule] = {}
        rules_by_parser: dict[Parser, Rule] = {}
        for gr in rules:
            check.not_in(gr, rules_set)
            check.not_in(gr._name, rules_by_name)  # noqa
            check.not_in(gr._name_f, rules_by_name_f)  # noqa
            check.not_in(gr._parser, rules_by_parser)  # noqa
            rules_by_name[gr._name] = gr  # noqa
            rules_by_name_f[gr._name_f] = gr  # noqa
            rules_by_parser[gr._parser] = gr  # noqa
        self._rules = rules_set
        self._rules_by_name: ta.Mapping[str, Rule] = rules_by_name
        self._rules_by_name_f: ta.Mapping[str, Rule] = rules_by_name_f
        self._rules_by_parser: ta.Mapping[Parser, Rule] = rules_by_parser

        if isinstance(root, str):
            root = rules_by_name_f[root.casefold()]
        self._root = root

    @property
    def root(self) -> Rule | None:
        return self._root

    def rule(self, name: str) -> Rule | None:
        return self._rules_by_name_f.get(name.casefold())

    def iter_parse(
            self,
            source: str,
            root: Rule | str | None = None,
            *,
            start: int = 0,
            debug: bool = False,
    ) -> ta.Iterator[Match]:
        if root is None:
            if (root := self._root) is None:
                raise AbnfError('No root or default root specified')
        else:
            if isinstance(root, str):
                root = self._rules_by_name_f[root.casefold()]
            else:
                root = check.in_(check.isinstance(root, Rule), self._rules)

        ctx_cls: type[_Context]
        if debug:
            ctx_cls = _DebugContext
        else:
            ctx_cls = _Context
        ctx = ctx_cls(self, source)

        return ctx.iter_parse(root._parser, start)  # noqa

    def parse(
            self,
            source: str,
            root: str | None = None,
            *,
            start: int = 0,
            debug: bool = False,
    ) -> Match | None:
        return longest_match(self.iter_parse(
            source,
            root,
            start=start,
            debug=debug,
        ))


##


class _Context:
    def __init__(
            self,
            grammar: Grammar,
            source: str,
    ) -> None:
        super().__init__()

        self._grammar = grammar
        self._source = source

    @property
    def grammar(self) -> Grammar:
        return self._grammar

    @property
    def source(self) -> str:
        return self._source

    def iter_parse(self, parser: Parser, start: int) -> ta.Iterator[Match]:
        return parser._iter_parse(self, start)  # noqa


class _DebugContext(_Context):
    _level: int = 0

    def iter_parse(self, parser: Parser, start: int) -> ta.Iterator[Match]:
        print(f'{"  " * self._level}enter: {parser=} {start=}')
        try:
            self._level += 1
            for m in super().iter_parse(parser, start):  # noqa
                # print(f'{"  " * (self._level - 1)}match: {parser=} {start=}')
                yield m
        finally:
            self._level -= 1
            print(f'{"  " * self._level}exit: {parser=} {start=}')


##


def iter_parse(
        obj: Grammar | Rule | Parser,
        src: str,
        *,
        root: str | None = None,
        start: int = 0,
) -> ta.Iterator[Match]:
    if isinstance(obj, Grammar):
        gram = obj
    elif isinstance(obj, Rule):
        check.none(root)
        gram = Grammar(obj, root=obj)
    elif isinstance(obj, Parser):
        check.none(root)
        gram = Grammar(Rule('root', obj), root='root')
    else:
        raise TypeError(obj)

    return gram.iter_parse(
        src,
        root,
        start=start,
    )


def parse(
        obj: Grammar | Rule | Parser,
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
