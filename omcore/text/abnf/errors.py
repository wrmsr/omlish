import typing as ta

from .positions import format_offset


##


class AbnfError(Exception):
    pass


##


class AbnfGrammarError(AbnfError):
    """An error in the definition of a grammar itself."""


class AbnfUnknownRuleError(AbnfGrammarError):
    """A reference to a rule not present in the grammar - either a RuleRef in a rule body or a requested root."""

    def __init__(self, names: ta.Mapping[str, ta.Iterable[str]] | str) -> None:
        if isinstance(names, str):
            names = {names: ()}
        self._names: ta.Mapping[str, tuple[str, ...]] = {n: tuple(rs) for n, rs in names.items()}

        super().__init__('Unknown rules: ' + ', '.join(
            repr(n) + (f' (referenced by {", ".join(map(repr, rs))})' if rs else '')
            for n, rs in self._names.items()
        ))

    @property
    def names(self) -> ta.Mapping[str, tuple[str, ...]]:
        return self._names


class AbnfGrammarParseError(AbnfError):
    """Failure to parse the text of a grammar definition."""


class AbnfTokenizationError(AbnfGrammarError):
    """A grammar cannot be given a token-level (lexed) interpretation - and why."""

    def __init__(self, msg: str, *, rule: str | None = None) -> None:
        self._rule = rule

        super().__init__(f'{f"Rule {rule!r}: " if rule is not None else ""}{msg}')

    @property
    def rule(self) -> str | None:
        return self._rule


##


class AbnfLrConflictError(AbnfGrammarError):
    """The grammar is not LALR(1): parse-table construction found shift/reduce or reduce/reduce conflicts."""

    def __init__(self, conflicts: ta.Sequence[str]) -> None:
        self._conflicts = tuple(conflicts)

        super().__init__('\n\n'.join([
            f'Grammar is not LALR(1) - {len(self._conflicts)} conflict(s):',
            *self._conflicts,
        ]))

    @property
    def conflicts(self) -> tuple[str, ...]:
        return self._conflicts


##


class AbnfEngineError(AbnfError):
    pass


class AbnfEngineCapabilityError(AbnfEngineError):
    """A requested behavior is outside the engine's declared capabilities."""


##


class AbnfParseError(AbnfError):
    """An error encountered while parsing a source text against a grammar."""


class AbnfIncompleteParseError(AbnfParseError):
    def __init__(
            self,
            msg: str | None = None,
            *,
            source: str | None = None,
            start: int | None = None,
            match_end: int | None = None,
            furthest_offset: int | None = None,
            rule_trace: ta.Sequence[str] | None = None,
    ) -> None:
        self._source = source
        self._start = start
        self._match_end = match_end
        self._furthest_offset = furthest_offset
        self._rule_trace = tuple(rule_trace) if rule_trace is not None else None

        if msg is None:
            parts = ['Incomplete parse' if match_end is not None else 'No parse']
            if furthest_offset is not None:
                fs = f'furthest match end at offset {furthest_offset}'
                if source is not None:
                    fs += f' ({format_offset(source, furthest_offset)})'
                parts.append(fs)
            if self._rule_trace:
                parts.append(f'in rules {" > ".join(self._rule_trace)}')
            msg = ': '.join([parts[0], ', '.join(parts[1:])]) if len(parts) > 1 else parts[0]

        super().__init__(msg)

    @property
    def source(self) -> str | None:
        return self._source

    @property
    def start(self) -> int | None:
        return self._start

    @property
    def match_end(self) -> int | None:
        return self._match_end

    @property
    def furthest_offset(self) -> int | None:
        return self._furthest_offset

    @property
    def rule_trace(self) -> tuple[str, ...] | None:
        return self._rule_trace


class AbnfMaxStepsExceededError(AbnfParseError):
    def __init__(self, steps: int) -> None:
        self._steps = steps

        super().__init__(f'Max steps exceeded: {steps}')

    @property
    def steps(self) -> int:
        return self._steps


class AbnfUnexpectedTokenError(AbnfParseError):
    def __init__(
            self,
            msg: str | None = None,
            *,
            source: str | None = None,
            offset: int | None = None,
            got: str | None = None,
            expected: ta.Sequence[str] | None = None,
    ) -> None:
        self._source = source
        self._offset = offset
        self._got = got
        self._expected = tuple(expected) if expected is not None else None

        if msg is None:
            msg = f'Unexpected {got}' if got is not None else 'Unexpected end of input'
            if offset is not None:
                msg += f' at offset {offset}'
                if source is not None:
                    msg += f' ({format_offset(source, offset)})'
            if self._expected:
                msg += f', expected {", ".join(self._expected)}'

        super().__init__(msg)

    @property
    def source(self) -> str | None:
        return self._source

    @property
    def offset(self) -> int | None:
        return self._offset

    @property
    def got(self) -> str | None:
        return self._got

    @property
    def expected(self) -> tuple[str, ...] | None:
        return self._expected


class AbnfLexError(AbnfParseError):
    def __init__(
            self,
            msg: str | None = None,
            *,
            source: str | None = None,
            offset: int | None = None,
    ) -> None:
        self._source = source
        self._offset = offset

        if msg is None:
            msg = 'No token matches'
            if offset is not None:
                msg += f' at offset {offset}'
                if source is not None:
                    msg += f' ({format_offset(source, offset)})'

        super().__init__(msg)

    @property
    def source(self) -> str | None:
        return self._source

    @property
    def offset(self) -> int | None:
        return self._offset
