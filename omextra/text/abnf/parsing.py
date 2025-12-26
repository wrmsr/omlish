import typing as ta

from .base import Match


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

    def iter_parse(self, op: Op, start: int) -> ta.Iterator[Match]:
        return parser._iter_parse(self, start)  # noqa


class _DebugContext(_Context):
    def __init__(
            self,
            grammar: Grammar,
            source: str,
            level: int = 1,
            *,
            write: ta.Callable[[str], None] | None = None,
    ) -> None:
        super().__init__(grammar, source)

        self._level = level
        if write is None:
            write = print
        self._write = write

        self._parser_strs: dict[Parser, str] = {}

    def _parser_str(self, parser: Parser) -> str:
        try:
            return self._parser_strs[parser]
        except KeyError:
            pass
        ps = self._parser_strs[parser] = str(parser)
        return ps

    _depth: int = 0

    def iter_parse(self, parser: Parser, start: int) -> ta.Iterator[Match]:
        if self._level < 2 and not isinstance(parser, ops.RuleRef):
            yield from super().iter_parse(parser, start)
            return

        ws = f'{"  " * self._depth} '

        if self._level < 2:
            ps = check.isinstance(parser, ops.RuleRef).name
        else:
            ps = self._parser_str(parser)
        body = f'{start}:{self._source[start]!r} {ps}'

        if self._level > 2:
            self._write(f'{ws}+ {body}')
        else:
            self._write(f'{ws}{body}')

        try:
            self._depth += 1

            for m in super().iter_parse(parser, start):  # noqa
                if self._level > 3:
                    self._write(f'{ws}! {m.start}-{m.end}:{self._source[m.start:m.end]!r}')

                yield m

        finally:
            self._depth -= 1

            if self._level > 3:
                self._write(f'{ws}- {body}')


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


##


class _StringLiteral:
    def _iter_parse(self, ctx: _Context, start: int) -> ta.Iterator[Match]:
        if start < len(ctx._source):  # noqa
            source = ctx._source[start : start + len(self._value)]  # noqa
            if source == self._value:
                yield Match(self, start, start + len(source), ())


class _CaseInsensitiveStringLiteral:
    def _iter_parse(self, ctx: _Context, start: int) -> ta.Iterator[Match]:
        if start < len(ctx._source):  # noqa
            source = ctx._source[start : start + len(self._value)].casefold()  # noqa
            if source == self._value:
                yield Match(self, start, start + len(source), ())


class _RangeLiteral:
    def _iter_parse(self, ctx: _Context, start: int) -> ta.Iterator[Match]:
        try:
            source = ctx._source[start]  # noqa
        except IndexError:
            return
        # ranges are always case-sensitive
        if (value := self._value).lo <= source <= value.hi:
            yield Match(self, start, start + 1, ())


class _Concat:
    def _iter_parse(self, ctx: _Context, start: int) -> ta.Iterator[Match]:
        i = 0
        match_tups: list[tuple[Match, ...]] = [()]
        for cp in self._children:
            next_match_tups: list[tuple[Match, ...]] = []
            for mt in match_tups:
                for cm in ctx.iter_parse(cp, mt[-1].end if mt else start):
                    next_match_tups.append((*mt, cm))
                    i += 1
            if not next_match_tups:
                return
            match_tups = next_match_tups
        if not i:
            return
        for mt in sorted(match_tups, key=len, reverse=True):
            yield Match(self, start, mt[-1].end if mt else start, mt)


class _Repeat:
    def _iter_parse(self, ctx: _Context, start: int) -> ta.Iterator[Match]:
        match_tup_set: set[tuple[Match, ...]] = set()
        last_match_tup_set: set[tuple[Match, ...]] = {()}
        i = 0
        while True:
            if self._times.max is not None and i == self._times.max:
                break
            next_match_tup_set: set[tuple[Match, ...]] = set()
            for mt in last_match_tup_set:
                for cm in ctx.iter_parse(self._child, mt[-1].end if mt else start):
                    next_match_tup_set.add((*mt, cm))
            if not next_match_tup_set or next_match_tup_set < match_tup_set:
                break
            i += 1
            match_tup_set |= next_match_tup_set
            last_match_tup_set = next_match_tup_set
        if i < self._times.min:
            return
        for mt in sorted(match_tup_set or [()], key=len, reverse=True):
            yield Match(self, start, mt[-1].end if mt else start, mt)  # noqa


class _Either:
    def _iter_parse(self, ctx: _Context, start: int) -> ta.Iterator[Match]:
        for cp in self._children:
            found = False
            for cm in ctx.iter_parse(cp, start):
                found = True
                yield Match(self, start, cm.end, (cm,))
            if found and self._first_match:
                return

class _RuleRef:
    def _iter_parse(self, ctx: _Context, start: int) -> ta.Iterator[Match]:
        cp = ctx._grammar._rules_by_name_f[self._name_f].parser  # noqa
        for cm in ctx.iter_parse(cp, start):
            yield Match(self, cm.start, cm.end, (cm,))
