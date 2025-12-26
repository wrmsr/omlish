import typing as ta

from omlish import check

from .base import Grammar
from .base import Match
from .base import Op
from .internal import Regex
from .ops import CaseInsensitiveStringLiteral
from .ops import Concat
from .ops import Either
from .ops import RangeLiteral
from .ops import Repeat
from .ops import RuleRef
from .ops import StringLiteral


##


class _Parser:
    def __init__(
            self,
            grammar: Grammar,
            source: str,
    ) -> None:
        super().__init__()

        self._grammar = grammar
        self._source = source

        self._dispatch: dict[type[Op], ta.Any] = {
            StringLiteral: self._iter_parse_string_literal,
            CaseInsensitiveStringLiteral: self._iter_parse_case_insensitive_string_literal,
            RangeLiteral: self._iter_parse_range_literal,
            Concat: self._iter_parse_concat,
            Repeat: self._iter_parse_repeat,
            Either: self._iter_parse_either,
            RuleRef: self._iter_parse_rule_ref,
            Regex: self._iter_parse_regex,
        }

    def _iter_parse_string_literal(self, op: StringLiteral, start: int) -> ta.Iterator[Match]:
        if start < len(self._source):  # noqa
            source = self._source[start : start + len(op._value)]  # noqa
            if source == op._value:  # noqa
                yield Match(op, start, start + len(source), ())

    def _iter_parse_case_insensitive_string_literal(self, op: CaseInsensitiveStringLiteral, start: int) -> ta.Iterator[Match]:  # noqa
        if start < len(self._source):  # noqa
            source = self._source[start : start + len(op._value)].casefold()  # noqa
            if source == op._value:  # noqa
                yield Match(op, start, start + len(source), ())

    def _iter_parse_range_literal(self, op: RangeLiteral, start: int) -> ta.Iterator[Match]:
        try:
            source = self._source[start]  # noqa
        except IndexError:
            return
        # ranges are always case-sensitive
        if (value := op._value).lo <= source <= value.hi:  # noqa
            yield Match(op, start, start + 1, ())

    def _iter_parse_concat(self, op: Concat, start: int) -> ta.Iterator[Match]:
        i = 0
        match_tups: list[tuple[Match, ...]] = [()]
        for cp in op._children:  # noqa
            next_match_tups: list[tuple[Match, ...]] = []
            for mt in match_tups:
                for cm in self.iter_parse(cp, mt[-1].end if mt else start):
                    next_match_tups.append((*mt, cm))
                    i += 1
            if not next_match_tups:
                return
            match_tups = next_match_tups
        if not i:
            return
        for mt in sorted(match_tups, key=len, reverse=True):
            yield Match(op, start, mt[-1].end if mt else start, mt)

    def _iter_parse_repeat(self, op: Repeat, start: int) -> ta.Iterator[Match]:
        match_tup_set: set[tuple[Match, ...]] = set()
        last_match_tup_set: set[tuple[Match, ...]] = {()}
        i = 0
        while True:
            if op._times.max is not None and i == op._times.max:  # noqa
                break
            next_match_tup_set: set[tuple[Match, ...]] = set()
            for mt in last_match_tup_set:
                for cm in self.iter_parse(op._child, mt[-1].end if mt else start):  # noqa
                    next_match_tup_set.add((*mt, cm))
            if not next_match_tup_set or next_match_tup_set < match_tup_set:
                break
            i += 1
            match_tup_set |= next_match_tup_set
            last_match_tup_set = next_match_tup_set
        if i < op._times.min:  # noqa
            return
        for mt in sorted(match_tup_set or [()], key=len, reverse=True):
            yield Match(op, start, mt[-1].end if mt else start, mt)  # noqa

    def _iter_parse_either(self, op: Either, start: int) -> ta.Iterator[Match]:
        for cp in op._children:  # noqa
            found = False
            for cm in self.iter_parse(cp, start):
                found = True
                yield Match(op, start, cm.end, (cm,))
            if found and op._first_match:  # noqa
                return

    def _iter_parse_rule_ref(self, op: RuleRef, start: int) -> ta.Iterator[Match]:
        cp = self._grammar._rules_by_name_f[op._name_f].op  # noqa
        for cm in self.iter_parse(cp, start):
            yield Match(op, cm.start, cm.end, (cm,))

    def _iter_parse_regex(self, op: Regex, start: int) -> ta.Iterator[Match]:
        raise NotImplementedError

    def iter_parse(self, op: Op, start: int) -> ta.Iterator[Match]:
        return self._dispatch[op.__class__](op, start)


##


class _DebugParser(_Parser):
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

        self._op_strs: dict[Op, str] = {}

    def _op_str(self, op: Op) -> str:
        try:
            return self._op_strs[op]
        except KeyError:
            pass
        ps = self._op_strs[op] = str(op)
        return ps

    _depth: int = 0

    def iter_parse(self, op: Op, start: int) -> ta.Iterator[Match]:
        if self._level < 2 and not isinstance(op, RuleRef):
            yield from super().iter_parse(op, start)
            return

        ws = f'{"  " * self._depth} '

        if self._level < 2:
            ps = check.isinstance(op, RuleRef).name
        else:
            ps = self._op_str(op)
        body = f'{start}:{self._source[start]!r} {ps}'

        if self._level > 2:
            self._write(f'{ws}+ {body}')
        else:
            self._write(f'{ws}{body}')

        try:
            self._depth += 1

            for m in super().iter_parse(op, start):  # noqa
                if self._level > 3:
                    self._write(f'{ws}! {m.start}-{m.end}:{self._source[m.start:m.end]!r}')

                yield m

        finally:
            self._depth -= 1

            if self._level > 3:
                self._write(f'{ws}- {body}')


##


def _iter_parse(
        grammar: Grammar,
        source: str,
        op: Op,
        start: int,
        *,
        debug: int = 0,
) -> ta.Iterator[Match]:
    parser: _Parser
    if debug:
        parser = _DebugParser(
            grammar,
            source,
            level=debug,
        )
    else:
        parser = _Parser(
            grammar,
            source,
        )

    return parser.iter_parse(op, start)
