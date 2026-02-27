import abc
import typing as ta

from ... import check
from ... import lang
from .base import Op
from .grammars import Grammar
from .grammars import Rule
from .internal import Regex
from .matches import Match
from .matches import furthest_match
from .matches import longest_match
from .ops import CaseInsensitiveStringLiteral
from .ops import Concat
from .ops import Either
from .ops import RangeLiteral
from .ops import Repeat
from .ops import RuleRef
from .ops import StringLiteral


##

class _Parser(lang.Abstract):
    class MaxStepsExceededError(Exception):
        pass

    @abc.abstractmethod
    def iter_parse(self, op: Op, start: int) -> ta.Iterator[Match]:
        raise NotImplementedError


##


_ParserContext: ta.TypeAlias = tuple[Op, int, ta.Optional['_ParserContext']]


class _ParserImpl(_Parser):
    """
    Packrat-ish-but-non-deterministic? 'Chart' parser?:
    - Top-down
    - Recursive descent
    - Memoized
    - Non-deterministic (yields all possible matches by default unless `Either.first_match`)
    """

    def __init__(
            self,
            grammar: Grammar,
            source: str,
            *,
            max_steps: int | None = None,
    ) -> None:
        super().__init__()

        self._grammar = grammar
        self._source = source
        self._max_steps = max_steps

        self._rules = self._grammar._rules  # Noqa

        self._dispatch: dict[type[Op], ta.Callable[[_ParserContext], ta.Iterator[Match]]] = ta.cast(ta.Any, {  # noqa
            StringLiteral: self._iter_parse_string_literal,
            CaseInsensitiveStringLiteral: self._iter_parse_case_insensitive_string_literal,
            RangeLiteral: self._iter_parse_range_literal,
            Concat: self._iter_parse_concat,
            Repeat: self._iter_parse_repeat,
            Either: self._iter_parse_either,
            RuleRef: self._iter_parse_rule_ref,
            Regex: self._iter_parse_regex,
        })

        self._memo: dict[tuple[Op, int], tuple[Match, ...]] = {}
        self._furthest: _ParserImpl._Furthest | None = None

        self._cur_step = 0

    class _Furthest(ta.NamedTuple):
        op: Op
        match: Match
        ctx: _ParserContext

    def _iter_parse_string_literal(self, ctx: _ParserContext) -> ta.Iterator[Match]:
        op: StringLiteral
        op, start, _ = ctx  # type: ignore[assignment]

        if start < len(self._source):  # noqa
            source = self._source[start : start + len(op._value)]  # noqa
            if source == op._value:  # noqa
                yield Match(op, start, start + len(source), ())

    def _iter_parse_case_insensitive_string_literal(self, ctx: _ParserContext) -> ta.Iterator[Match]:  # noqa
        op: CaseInsensitiveStringLiteral
        op, start, _ = ctx  # type: ignore[assignment]

        if start < len(self._source):  # noqa
            source = self._source[start : start + len(op._value)].casefold()  # noqa
            if source == op._value:  # noqa
                yield Match(op, start, start + len(source), ())

    def _iter_parse_range_literal(self, ctx: _ParserContext) -> ta.Iterator[Match]:
        op: RangeLiteral
        op, start, _ = ctx  # type: ignore[assignment]

        try:
            source = self._source[start]  # noqa
        except IndexError:
            return

        # ranges are always case-sensitive
        if (value := op._value).lo <= source <= value.hi:  # noqa
            yield Match(op, start, start + 1, ())

    def _iter_parse_concat(self, ctx: _ParserContext) -> ta.Iterator[Match]:
        op: Concat
        op, start, _ = ctx  # type: ignore[assignment]

        match_tups: list[tuple[Match, ...]] = [()]

        i = 0
        for cp in op._children:  # noqa
            next_match_tups: list[tuple[Match, ...]] = []

            for mt in match_tups:
                for cm in self._iter_parse((cp, mt[-1].end if mt else start, ctx)):
                    next_match_tups.append((*mt, cm))
                    i += 1

            if not next_match_tups:
                return

            match_tups = next_match_tups

        if not i:
            return

        for mt in sorted(match_tups, key=len, reverse=True):
            yield Match(op, start, mt[-1].end if mt else start, mt)

    def _iter_parse_repeat(self, ctx: _ParserContext) -> ta.Iterator[Match]:
        op: Repeat
        op, start, _ = ctx  # type: ignore[assignment]

        # Map from (repetition_count, end_position) to longest match tuple
        matches_by_count_pos: dict[tuple[int, int], tuple[Match, ...]] = {(0, start): ()}
        max_end_by_count: dict[int, int] = {0: start}

        i = 0
        while True:
            if op._times.max is not None and i == op._times.max:  # noqa
                break

            if self._max_steps is not None and self._cur_step > self._max_steps:
                raise _Parser.MaxStepsExceededError(self._cur_step)
            self._cur_step += 1

            next_matches: dict[tuple[int, int], tuple[Match, ...]] = {}
            next_max_end = max_end_by_count.get(i, -1)

            for (count, end_pos), mt in matches_by_count_pos.items():
                if count != i:
                    continue

                for cm in self._iter_parse((op._child, end_pos, ctx)):  # noqa
                    next_mt = (*mt, cm)
                    next_key = (i + 1, cm.end)

                    # Keep only the longest match tuple for each (count, position)
                    if next_key not in next_matches or len(next_mt) > len(next_matches[next_key]):
                        next_matches[next_key] = next_mt
                        if cm.end > next_max_end:
                            next_max_end = cm.end

            if not next_matches:
                break

            # Check if we made progress (reached new positions)
            if next_max_end <= max_end_by_count.get(i, -1):
                break

            i += 1
            matches_by_count_pos.update(next_matches)
            max_end_by_count[i] = next_max_end

        if i < op._times.min:  # noqa
            return

        # Collect valid matches and sort by (end_position, repetition_count) descending
        valid_matches: list[tuple[int, int, tuple[Match, ...]]] = []
        for (count, end_pos), mt in matches_by_count_pos.items():
            if op._times.min <= count <= (op._times.max if op._times.max is not None else i):  # noqa
                valid_matches.append((end_pos, count, mt))

        for end_pos, _, mt in sorted(valid_matches, key=lambda x: (x[0], x[1]), reverse=True):
            yield Match(op, start, end_pos, mt)

    def _iter_parse_either(self, ctx: _ParserContext) -> ta.Iterator[Match]:
        op: Either
        op, start, _ = ctx  # type: ignore[assignment]

        for cp in op._children:  # noqa
            found = False

            for cm in self._iter_parse((cp, start, ctx)):
                found = True
                yield Match(op, start, cm.end, (cm,))

            if found and op._first_match:  # noqa
                return

    def _iter_parse_rule_ref(self, ctx: _ParserContext) -> ta.Iterator[Match]:
        op: RuleRef
        op, start, _ = ctx  # type: ignore[assignment]

        cp = self._rules._rules_by_name_f[op._name_f].op  # noqa
        for cm in self._iter_parse((cp, start, ctx)):
            yield Match(op, cm.start, cm.end, (cm,))

    def _iter_parse_regex(self, ctx: _ParserContext) -> ta.Iterator[Match]:
        op: Regex
        op, start, _ = ctx  # type: ignore[assignment]

        if (m := op._pat.match(self._source, start)) is not None:  # noqa
            yield Match(op, start, m.end(), ())

    def _iter_parse(self, ctx: _ParserContext) -> ta.Iterator[Match]:
        op, start, _ = ctx

        if (key := (op, start)) in self._memo:
            yield from self._memo[key]
            return

        if self._max_steps is not None and self._cur_step >= self._max_steps:
            raise _Parser.MaxStepsExceededError(self._cur_step)
        self._cur_step += 1

        matches = tuple(self._dispatch[op.__class__](ctx))
        self._memo[key] = matches

        if matches and (fm := furthest_match(matches)) is not None:
            if self._furthest is None or fm.end > self._furthest.match.end:
                self._furthest = _ParserImpl._Furthest(op, fm, ctx)

        yield from matches

    def iter_parse(self, op: Op, start: int) -> ta.Iterator[Match]:
        return self._iter_parse((op, start, None))

##


class _DebugParserImpl(_ParserImpl):
    def __init__(
            self,
            grammar: Grammar,
            source: str,
            level: int = 1,
            *,
            write: ta.Callable[[str], None] | None = None,
            **kwargs: ta.Any,
    ) -> None:
        super().__init__(grammar, source, **kwargs)

        self._level = level
        if write is None:
            write = print
        self._write = write

        self._op_strs: dict[Op, str] = {}

    def _op_str(self, op: Op) -> str:
        try:
            return self._op_strs[op]
        except KeyError:
            pass
        ps = self._op_strs[op] = str(op)
        return ps

    _depth: int = 0

    def _iter_parse(self, ctx: _ParserContext) -> ta.Iterator[Match]:
        op, start, _ = ctx

        if self._level < 2 and not isinstance(op, RuleRef):
            yield from super()._iter_parse(ctx)
            return

        ws = f'{"  " * self._depth} '

        if self._level < 2:
            ps = check.isinstance(op, RuleRef).name
        else:
            ps = self._op_str(op)
        body = f'{start}:{self._source[start] if start < len(self._source) else ""!r} {ps}'

        if self._level > 2:
            self._write(f'{ws}+ {body}')
        else:
            self._write(f'{ws}{body}')

        try:
            self._depth += 1

            for m in super()._iter_parse(ctx):  # noqa
                if self._level > 3:
                    self._write(f'{ws}! {m.start}-{m.end}:{self._source[m.start:m.end]!r}')

                yield m

        finally:
            self._depth -= 1

            if self._level > 3:
                self._write(f'{ws}- {body}')


#


def _make_parser(
        grammar: Grammar,
        source: str,
        *,
        debug: int = 0,
        max_steps: int | None = None,
) -> _Parser:
    if debug:
        return _DebugParserImpl(
            grammar,
            source,
            max_steps=max_steps,
            level=debug,
        )
    else:
        return _ParserImpl(
            grammar,
            source,
            max_steps=max_steps,
        )


##


def iter_parse(
        obj: Grammar | Rule | Op,
        src: str,
        *,
        root: str | None = None,
        start: int = 0,
        debug: int = 0,
        max_steps: int | None = None,
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
        debug=debug,
        max_steps=max_steps,
    )


def parse(
        obj: Grammar | Rule | Op,
        src: str,
        *,
        root: str | None = None,
        start: int = 0,
        debug: int = 0,
        max_steps: int | None = None,
) -> Match | None:
    return longest_match(iter_parse(
        obj,
        src,
        root=root,
        start=start,
        debug=debug,
        max_steps=max_steps,
    ))
