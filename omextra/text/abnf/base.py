import io
import itertools
import typing as ta

from omlish import check
from omlish import lang

from .errors import AbnfError
from .errors import AbnfIncompleteParseError


with lang.auto_proxy_import(globals()):
    from . import ops
    from . import parsing


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
        if isinstance(o, (ops.StringLiteral, ops.CaseInsensitiveStringLiteral)):
            write(f'literal<{self.start}-{self.end}>({o.value!r})')
        elif isinstance(o, ops.RangeLiteral):
            write(f'literal<{self.start}-{self.end}>({o.value.lo!r}-{o.value.hi!r})')
        else:
            write(f'{o.__class__.__name__.lower()}<{self.start}-{self.end}>')
            if isinstance(o, ops.RuleRef):
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


class Op(lang.Abstract, lang.PackageSealed):
    def _match_repr(self) -> str:
        return f'{self.__class__.__name__}@{id(self):x}'


class LeafOp(Op, lang.Abstract):
    pass


##


class Rule(lang.Final):
    def __init__(
            self,
            name: str,
            op: Op,
            *,
            insignificant: bool = False,
    ) -> None:
        super().__init__()

        self._name = check.non_empty_str(name)
        self._name_f = name.casefold()
        self._op = check.isinstance(op, Op)
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
    def op(self) -> Op:
        return self._op

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
        rules_by_op: dict[Op, Rule] = {}
        for gr in rules:
            check.not_in(gr, rules_set)
            check.not_in(gr._name, rules_by_name)  # noqa
            check.not_in(gr._name_f, rules_by_name_f)  # noqa
            check.not_in(gr._op, rules_by_op)  # noqa
            rules_set.add(gr)
            rules_by_name[gr._name] = gr  # noqa
            rules_by_name_f[gr._name_f] = gr  # noqa
            rules_by_op[gr._op] = gr  # noqa
        self._rules = rules_set
        self._rules_by_name: ta.Mapping[str, Rule] = rules_by_name
        self._rules_by_name_f: ta.Mapping[str, Rule] = rules_by_name_f
        self._rules_by_op: ta.Mapping[Op, Rule] = rules_by_op

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
            debug: int = 0,
    ) -> ta.Iterator[Match]:
        if root is None:
            if (root := self._root) is None:
                raise AbnfError('No root or default root specified')
        else:
            if isinstance(root, str):
                root = self._rules_by_name_f[root.casefold()]
            else:
                root = check.in_(check.isinstance(root, Rule), self._rules)

        return parsing._iter_parse(  # noqa
            self,
            source,
            root._op,  # noqa
            start,
            debug=debug,
        )

    def parse(
            self,
            source: str,
            root: str | None = None,
            *,
            start: int = 0,
            complete: bool = False,
            debug: int = 0,
    ) -> Match | None:
        if (match := longest_match(self.iter_parse(
            source,
            root,
            start=start,
            debug=debug,
        ))) is None:
            return None

        if complete and (match.start, match.end) != (start, len(source)):
            raise AbnfIncompleteParseError

        return match


##


def iter_parse(
        obj: Grammar | Rule | Op,
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
    elif isinstance(obj, Op):
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
        obj: Grammar | Rule | Op,
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
