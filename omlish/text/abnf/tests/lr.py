# @omlish-precheck-allow-any-unicode
"""
~~vIbEd~~ lol

LR/LALR table-driven parser implementation for ABNF grammars.

This module provides an alternative parsing backend using bottom-up LR parsing with pre-computed ACTION/GOTO tables. The
parser converts Op trees into a CFG, builds LR(0) item sets, and uses SLR(1) lookahead for parsing.
"""
import collections
import dataclasses as dc
import typing as ta

from .... import check
from .... import lang
from ..base import Op
from ..grammars import Grammar
from ..internal import Regex
from ..matches import Match
from ..ops import CaseInsensitiveStringLiteral
from ..ops import Concat
from ..ops import Either
from ..ops import RangeLiteral
from ..ops import Repeat
from ..ops import RuleRef
from ..ops import StringLiteral
from ..parsing import _Parser


##
# CFG Representation


@dc.dataclass(frozen=True)
class Symbol(lang.Abstract):
    """Base class for grammar symbols (terminals and non-terminals)."""


@dc.dataclass(frozen=True)
class Terminal(Symbol):
    """Terminal symbol (token)."""

    op: Op  # The original Op this terminal represents

    def __repr__(self) -> str:
        return f'Terminal({self.op._match_repr()})'  # noqa


@dc.dataclass(frozen=True)
class NonTerminal(Symbol):
    """Non-terminal symbol (variable)."""

    name: str
    op: Op  # The original Op this non-terminal represents

    def __repr__(self) -> str:
        return f'NT({self.name})'


@dc.dataclass(frozen=True)
class Epsilon(Symbol):
    """Empty string symbol."""

    def __repr__(self) -> str:
        return 'ε'


EPSILON = Epsilon()

EOF = Terminal(op=None)  # type: ignore  # Sentinel for end of input


@dc.dataclass(frozen=True)
class Production:
    """CFG production rule: lhs → rhs."""

    lhs: NonTerminal
    rhs: tuple[Symbol, ...]  # Sequence of symbols
    original_op: Op  # The original Op this production represents

    def __repr__(self) -> str:
        rhs_str = ' '.join(str(s) for s in self.rhs) if self.rhs else 'ε'
        return f'{self.lhs} → {rhs_str}'


class Cfg:
    """Context-Free Grammar representation."""

    def __init__(
            self,
            productions: list[Production],
            start: NonTerminal,
    ) -> None:
        self.productions = productions
        self.start = start

        # Build indices for efficient lookup
        self.productions_by_lhs: dict[NonTerminal, list[Production]] = collections.defaultdict(list)
        for prod in productions:
            self.productions_by_lhs[prod.lhs].append(prod)

        # Collect all symbols
        self.non_terminals: set[NonTerminal] = {start}
        self.terminals: set[Terminal] = set()

        for prod in productions:
            self.non_terminals.add(prod.lhs)
            for sym in prod.rhs:
                if isinstance(sym, NonTerminal):
                    self.non_terminals.add(sym)
                elif isinstance(sym, Terminal):
                    self.terminals.add(sym)


##
# Op to CFG Conversion


class OpToCfgConverter:
    """Converts Op trees into CFG productions."""

    def __init__(self) -> None:
        self.productions: list[Production] = []
        self.next_nt_id = 0
        self.op_to_nt: dict[int, NonTerminal] = {}  # Map op id to non-terminal

    def _fresh_nt(self, op: Op, name: str | None = None) -> NonTerminal:
        """Generate a fresh non-terminal for an Op."""

        if name is None:
            name = f'_G{self.next_nt_id}'
            self.next_nt_id += 1
        return NonTerminal(name=name, op=op)

    def convert_grammar(self, grammar: Grammar, root_rule_name: str) -> Cfg:
        """Convert a Grammar to CFG."""

        root_rule = grammar.rule(root_rule_name)
        root_rule = check.not_none(root_rule, f'Root rule {root_rule_name!r} not found')

        # Create start symbol
        start_nt = self._fresh_nt(root_rule.op, name=root_rule.name)

        # Convert the root rule
        self._convert_op(root_rule.op, start_nt)

        return Cfg(self.productions, start_nt)

    def _convert_op(self, op: Op, lhs: NonTerminal) -> None:
        """Convert an Op to productions with given lhs."""

        if isinstance(op, (StringLiteral, CaseInsensitiveStringLiteral, RangeLiteral, Regex)):
            # Literals are terminals
            term = Terminal(op=op)
            self.productions.append(Production(lhs=lhs, rhs=(term,), original_op=op))

        elif isinstance(op, RuleRef):
            # RuleRef becomes a reference to another non-terminal
            # We'll resolve this lazily - create a new NT if not seen before
            op_id = id(op)
            if op_id not in self.op_to_nt:
                ref_nt = self._fresh_nt(op, name=op.name)
                self.op_to_nt[op_id] = ref_nt
                # Note: We don't expand RuleRef here - the grammar must provide the rule
                # For now, create a placeholder production
                # In a real implementation, we'd resolve this from the Grammar
            else:
                ref_nt = self.op_to_nt[op_id]

            self.productions.append(Production(lhs=lhs, rhs=(ref_nt,), original_op=op))

        elif isinstance(op, Concat):
            # Concat becomes a sequence of symbols
            rhs_symbols: list[Symbol] = []
            for child in op.children:
                child_nt = self._fresh_nt(child)
                self._convert_op(child, child_nt)
                rhs_symbols.append(child_nt)

            self.productions.append(Production(lhs=lhs, rhs=tuple(rhs_symbols), original_op=op))

        elif isinstance(op, Either):
            # Either becomes multiple productions
            for child in op.children:
                child_nt = self._fresh_nt(child)
                self._convert_op(child, child_nt)
                self.productions.append(Production(lhs=lhs, rhs=(child_nt,), original_op=op))

        elif isinstance(op, Repeat):
            # Repeat becomes recursive productions
            # A → ε | item A  (for min=0, max=None)
            # For bounded repeats, we'd need to generate multiple productions

            child_nt = self._fresh_nt(op.child)
            self._convert_op(op.child, child_nt)

            times = op.times

            if times.min == 0 and times.max is None:
                # A → ε | item A
                self.productions.append(Production(lhs=lhs, rhs=(EPSILON,), original_op=op))
                self.productions.append(Production(lhs=lhs, rhs=(child_nt, lhs), original_op=op))

            elif times.min == 1 and times.max is None:
                # A → item | item A
                self.productions.append(Production(lhs=lhs, rhs=(child_nt,), original_op=op))
                self.productions.append(Production(lhs=lhs, rhs=(child_nt, lhs), original_op=op))

            elif times.min == 0 and times.max == 1:
                # A → ε | item
                self.productions.append(Production(lhs=lhs, rhs=(EPSILON,), original_op=op))
                self.productions.append(Production(lhs=lhs, rhs=(child_nt,), original_op=op))

            else:
                # For bounded repeats, use a simplified approach
                # This is a limitation of simple CFG conversion
                # A proper implementation would generate intermediate non-terminals
                if times.max is None:
                    # A → item^min A'
                    # A' → ε | item A'
                    base_rhs = tuple(child_nt for _ in range(times.min))
                    tail_nt = self._fresh_nt(op, name=f'{lhs.name}_tail')

                    self.productions.append(Production(lhs=lhs, rhs=(*base_rhs, tail_nt), original_op=op))
                    self.productions.append(Production(lhs=tail_nt, rhs=(EPSILON,), original_op=op))
                    self.productions.append(Production(lhs=tail_nt, rhs=(child_nt, tail_nt), original_op=op))

                else:
                    # For fixed ranges, generate sequence
                    # This is exponential for large ranges - a known limitation
                    for count in range(times.min, (times.max or times.min) + 1):
                        rhs: tuple[Symbol, ...] = tuple(child_nt for _ in range(count))
                        if not rhs:
                            rhs = (EPSILON,)
                        self.productions.append(Production(lhs=lhs, rhs=rhs, original_op=op))

        else:
            raise TypeError(f'Unsupported Op type: {type(op)}')


##
# LR Item and Closure


@dc.dataclass(frozen=True)
class LrItem:
    """LR(0) item: [production, dot_position]."""

    production: Production
    dot_pos: int  # Position of the dot in rhs

    @property
    def symbol_after_dot(self) -> Symbol | None:
        """Get the symbol immediately after the dot, or None if at end."""

        if self.dot_pos < len(self.production.rhs):
            return self.production.rhs[self.dot_pos]
        return None

    @property
    def is_complete(self) -> bool:
        """Check if dot is at the end (complete item)."""

        return self.dot_pos >= len(self.production.rhs)

    def advance(self) -> 'LrItem':
        """Return a new item with dot advanced by one position."""

        return LrItem(self.production, self.dot_pos + 1)

    def __repr__(self) -> str:
        rhs_parts = []
        for i, sym in enumerate(self.production.rhs):
            if i == self.dot_pos:
                rhs_parts.append('•')
            rhs_parts.append(str(sym))
        if self.dot_pos >= len(self.production.rhs):
            rhs_parts.append('•')

        rhs_str = ' '.join(rhs_parts) if rhs_parts else '•'
        return f'[{self.production.lhs} → {rhs_str}]'


class LrAutomaton:
    """Builds LR(0) automaton (canonical collection of item sets)."""

    def __init__(self, cfg: Cfg) -> None:
        self.cfg = cfg
        self.item_sets: list[frozenset[LrItem]] = []
        self.goto_table: dict[tuple[int, Symbol], int] = {}  # (state, symbol) → state

        self._build_automaton()

    def _closure(self, items: ta.Iterable[LrItem]) -> frozenset[LrItem]:
        """Compute closure of a set of items."""

        closure_set = set(items)
        added = True

        while added:
            added = False
            for item in list(closure_set):
                sym = item.symbol_after_dot
                if isinstance(sym, NonTerminal):
                    # Add all productions for this non-terminal
                    for prod in self.cfg.productions_by_lhs[sym]:
                        new_item = LrItem(prod, 0)
                        if new_item not in closure_set:
                            closure_set.add(new_item)
                            added = True

        return frozenset(closure_set)

    def _goto(self, items: frozenset[LrItem], symbol: Symbol) -> frozenset[LrItem]:
        """Compute goto(items, symbol)."""

        moved_items = set()

        for item in items:
            if item.symbol_after_dot == symbol:
                moved_items.add(item.advance())

        if not moved_items:
            return frozenset()

        return self._closure(moved_items)

    def _build_automaton(self) -> None:
        """Build the canonical collection of LR(0) item sets."""

        # Start with initial item set
        start_production = self.cfg.productions_by_lhs[self.cfg.start][0]
        initial_item = LrItem(start_production, 0)
        initial_set = self._closure([initial_item])

        self.item_sets = [initial_set]
        unprocessed = [0]  # Indices of unprocessed item sets
        set_to_index = {initial_set: 0}

        while unprocessed:
            current_idx = unprocessed.pop(0)
            current_set = self.item_sets[current_idx]

            # Find all symbols that appear after dots
            symbols_after_dot: set[Symbol] = set()
            for item in current_set:
                if (sym := item.symbol_after_dot) is not None:
                    symbols_after_dot.add(sym)

            # Compute goto for each symbol
            for symbol in symbols_after_dot:
                next_set = self._goto(current_set, symbol)

                if not next_set:
                    continue

                if next_set not in set_to_index:
                    # New item set
                    next_idx = len(self.item_sets)
                    self.item_sets.append(next_set)
                    set_to_index[next_set] = next_idx
                    unprocessed.append(next_idx)
                else:
                    next_idx = set_to_index[next_set]

                self.goto_table[(current_idx, symbol)] = next_idx


##
# FOLLOW Set Computation


class FollowSetComputer:
    """Computes FOLLOW sets for SLR(1) parsing."""

    def __init__(self, cfg: Cfg) -> None:
        self.cfg = cfg
        self.first_sets: dict[Symbol, set[Symbol]] = {}
        self.follow_sets: dict[NonTerminal, set[Terminal]] = collections.defaultdict(set)

        self._compute_first_sets()
        self._compute_follow_sets()

    def _compute_first_sets(self) -> None:
        """Compute FIRST sets for all symbols."""

        # Initialize
        for term in self.cfg.terminals:
            self.first_sets[term] = {term}

        self.first_sets[EPSILON] = {EPSILON}

        for nt in self.cfg.non_terminals:
            self.first_sets[nt] = set()

        # Iterate until no changes
        changed = True
        while changed:
            changed = False

            for prod in self.cfg.productions:
                lhs = prod.lhs
                rhs = prod.rhs

                if not rhs or rhs == (EPSILON,):
                    if EPSILON not in self.first_sets[lhs]:
                        self.first_sets[lhs].add(EPSILON)
                        changed = True
                else:
                    # Add FIRST of first symbol
                    first_sym = rhs[0]
                    before = len(self.first_sets[lhs])
                    self.first_sets[lhs] |= self.first_sets.get(first_sym, set()) - {EPSILON}
                    if len(self.first_sets[lhs]) > before:
                        changed = True

    def _compute_follow_sets(self) -> None:
        """Compute FOLLOW sets for all non-terminals."""

        # Start symbol has EOF in its FOLLOW set
        self.follow_sets[self.cfg.start].add(EOF)

        # Iterate until no changes
        changed = True
        while changed:
            changed = False

            for prod in self.cfg.productions:
                lhs = prod.lhs
                rhs = prod.rhs

                for i, sym in enumerate(rhs):
                    if not isinstance(sym, NonTerminal):
                        continue

                    # Look at symbols after this non-terminal
                    if i + 1 < len(rhs):
                        next_sym = rhs[i + 1]
                        before = len(self.follow_sets[sym])

                        if isinstance(next_sym, Terminal):
                            self.follow_sets[sym].add(next_sym)
                        elif isinstance(next_sym, NonTerminal):
                            first_next = self.first_sets.get(next_sym, set())
                            self.follow_sets[sym] |= first_next - {EPSILON}  # type: ignore[arg-type]

                            # If next can be epsilon, add FOLLOW(lhs) to FOLLOW(sym)
                            if EPSILON in first_next:
                                self.follow_sets[sym] |= self.follow_sets[lhs]

                        if len(self.follow_sets[sym]) > before:
                            changed = True
                    else:
                        # sym is last in production, add FOLLOW(lhs) to FOLLOW(sym)
                        before = len(self.follow_sets[sym])
                        self.follow_sets[sym] |= self.follow_sets[lhs]
                        if len(self.follow_sets[sym]) > before:
                            changed = True


##
# Parse Table Construction


@dc.dataclass()
class Action(lang.Abstract):
    """Base class for parsing actions."""


@dc.dataclass()
class Shift(Action):
    """Shift action: push symbol and go to state."""

    state: int


@dc.dataclass()
class Reduce(Action):
    """Reduce action: reduce by production."""

    production: Production


@dc.dataclass()
class Accept(Action):
    """Accept action: parsing complete."""


class ParseTable:
    """SLR(1) parse table with ACTION and GOTO."""

    def __init__(
            self,
            cfg: Cfg,
            automaton: LrAutomaton,
            follow_computer: FollowSetComputer,
    ) -> None:
        self.cfg = cfg
        self.automaton = automaton
        self.follow_computer = follow_computer

        self.action: dict[tuple[int, Terminal], list[Action]] = collections.defaultdict(list)
        self.goto: dict[tuple[int, NonTerminal], int] = {}

        self._build_table()

    def _build_table(self) -> None:
        """Build ACTION and GOTO tables."""

        for state_idx, item_set in enumerate(self.automaton.item_sets):
            for item in item_set:
                if not item.is_complete:
                    # Shift or goto
                    sym = item.symbol_after_dot
                    if (state_idx, sym) in self.automaton.goto_table:
                        next_state = self.automaton.goto_table[(state_idx, sym)]  # type: ignore[index]

                        if isinstance(sym, Terminal):
                            # Shift action
                            self.action[(state_idx, sym)].append(Shift(next_state))
                        elif isinstance(sym, NonTerminal):
                            # Goto entry
                            self.goto[(state_idx, sym)] = next_state

                else:
                    # Reduce action
                    prod = item.production

                    # Check if this is accepting state (reducing start production)
                    if prod.lhs == self.cfg.start and state_idx == 0:
                        self.action[(state_idx, EOF)].append(Accept())
                    else:
                        # Add reduce action for all symbols in FOLLOW(lhs)
                        follow = self.follow_computer.follow_sets[prod.lhs]
                        for terminal in follow:
                            self.action[(state_idx, terminal)].append(Reduce(prod))


##
# LR Parser Implementation


class _LrParser(_Parser):
    """LR table-driven parser implementation."""

    def __init__(
            self,
            grammar: Grammar,
            source: str,
            *,
            root_rule_name: str = 'root',
            **kwargs: ta.Any,
    ) -> None:
        super().__init__()

        self._grammar = grammar
        self._source = source

        # Pre-compute CFG and parse tables
        converter = OpToCfgConverter()
        self._cfg = converter.convert_grammar(grammar, root_rule_name)

        self._automaton = LrAutomaton(self._cfg)
        self._follow_computer = FollowSetComputer(self._cfg)
        self._parse_table = ParseTable(self._cfg, self._automaton, self._follow_computer)

    def _match_terminal(self, terminal: Terminal, pos: int) -> Match | None:
        """Try to match a terminal at the given position."""

        if terminal == EOF:
            if pos >= len(self._source):
                return Match(terminal.op, pos, pos, ())
            return None

        op = terminal.op

        if isinstance(op, StringLiteral):
            source = self._source[pos : pos + len(op._value)]  # noqa
            if source == op._value:  # noqa
                return Match(op, pos, pos + len(source), ())

        elif isinstance(op, CaseInsensitiveStringLiteral):
            source = self._source[pos : pos + len(op._value)].casefold()  # noqa
            if source == op._value:  # noqa
                return Match(op, pos, pos + len(source), ())

        elif isinstance(op, RangeLiteral):
            if pos < len(self._source):
                source_char = self._source[pos]
                if op._value.lo <= source_char <= op._value.hi:  # noqa
                    return Match(op, pos, pos + 1, ())

        elif isinstance(op, Regex):
            if (m := op._pat.match(self._source, pos)) is not None:  # noqa
                return Match(op, pos, m.end(), ())

        return None

    def _get_lookahead_terminals(self, pos: int) -> list[tuple[Terminal, Match]]:
        """Get all terminals that can match at the given position."""

        candidates: list[tuple[Terminal, Match]] = []

        # Try all known terminals
        for terminal in self._cfg.terminals:
            if (match := self._match_terminal(terminal, pos)) is not None:
                candidates.append((terminal, match))

        # Also try EOF
        if pos >= len(self._source):
            if (eof_match := self._match_terminal(EOF, pos)) is not None:
                candidates.append((EOF, eof_match))

        return candidates

    @dc.dataclass()
    class _StackEntry:
        state: int
        symbol: Symbol | None
        match: Match | None
        start_pos: int

    def iter_parse(self, op: Op, start: int) -> ta.Iterator[Match]:
        """Parse using LR table-driven approach with shift-reduce algorithm."""

        # Stack entries: (state, symbol, match, start_pos)
        # Initialize parse stack with start state
        stack: list[_LrParser._StackEntry] = [_LrParser._StackEntry(0, None, None, start)]

        # Track parse position
        pos = start

        # Shift-reduce parsing loop
        while True:
            current_state = stack[-1].state

            # Get lookahead terminals
            lookahead_candidates = self._get_lookahead_terminals(pos)

            if not lookahead_candidates:
                # No valid lookahead - parse error
                return

            # Try each lookahead (handles conflicts by exploring all paths)
            for lookahead_term, lookahead_match in lookahead_candidates:
                # Look up actions for this state and lookahead
                actions = self._parse_table.action.get((current_state, lookahead_term), [])

                if not actions:
                    continue

                for action in actions:
                    if isinstance(action, Shift):
                        # Shift: consume input and push state
                        new_stack = stack + [_LrParser._StackEntry(  # noqa
                            action.state,
                            lookahead_term,
                            lookahead_match,
                            pos,
                        )]

                        # Continue parsing with new stack and position
                        yield from self._continue_parse(new_stack, lookahead_match.end)

                    elif isinstance(action, Reduce):
                        # Reduce: pop items and build match
                        prod = action.production
                        rhs_len = len(prod.rhs) if prod.rhs != (EPSILON,) else 0

                        # Pop rhs_len items from stack
                        if rhs_len > len(stack) - 1:
                            continue  # Invalid reduction

                        popped = stack[-rhs_len:] if rhs_len > 0 else []
                        new_stack = stack[:-rhs_len] if rhs_len > 0 else stack

                        # Get goto state
                        goto_state = self._parse_table.goto.get((new_stack[-1].state, prod.lhs))
                        if goto_state is None:
                            continue  # No goto transition

                        # Build match from reduction
                        if rhs_len == 0:
                            # Epsilon production
                            reduced_match = Match(prod.original_op, pos, pos, ())
                        else:
                            # Build match from popped items
                            children = tuple(p.match for p in popped if p.match is not None)
                            match_start = popped[0].start_pos if popped else pos
                            match_end = popped[-1].match.end if popped and popped[-1].match else pos

                            reduced_match = Match(
                                prod.original_op,
                                match_start,
                                match_end,
                                children,
                            )

                        # Push reduced non-terminal
                        new_stack = new_stack + [_LrParser._StackEntry(  # noqa
                            goto_state,
                            prod.lhs,
                            reduced_match,
                            reduced_match.start,
                        )]

                        # Continue parsing with new stack (same position - we didn't consume input)
                        yield from self._continue_parse(new_stack, pos)

                    elif isinstance(action, Accept):
                        # Accept: parse complete!
                        if len(stack) >= 2 and stack[1].match is not None:
                            yield stack[1].match
                        return

            # If we get here, no actions succeeded - parse error
            return

    def _continue_parse(self, stack: list, pos: int) -> ta.Iterator[Match]:
        """Continue parsing from a given stack configuration."""

        # This is a helper to handle the recursive nature of exploring multiple parse paths
        # In a real implementation, this would be part of the main loop with proper state management

        # For now, we implement a simplified version that returns to the main loop
        # A full GLR-style implementation would fork parse states here

        # We'll just continue the main parsing logic inline for simplicity
        while True:
            current_state = stack[-1].state

            lookahead_candidates = self._get_lookahead_terminals(pos)
            if not lookahead_candidates:
                return

            found_action = False

            for lookahead_term, lookahead_match in lookahead_candidates:
                actions = self._parse_table.action.get((current_state, lookahead_term), [])

                if not actions:
                    continue

                found_action = True

                for action in actions:
                    if isinstance(action, Shift):
                        stack = stack + [type(stack[0])(  # noqa
                            action.state,
                            lookahead_term,
                            lookahead_match,
                            pos,
                        )]
                        pos = lookahead_match.end
                        break  # Continue outer loop

                    elif isinstance(action, Reduce):
                        prod = action.production
                        rhs_len = len(prod.rhs) if prod.rhs != (EPSILON,) else 0

                        if rhs_len > len(stack) - 1:
                            continue

                        popped = stack[-rhs_len:] if rhs_len > 0 else []
                        stack = stack[:-rhs_len] if rhs_len > 0 else stack

                        goto_state = self._parse_table.goto.get((stack[-1].state, prod.lhs))
                        if goto_state is None:
                            continue

                        if rhs_len == 0:
                            reduced_match = Match(prod.original_op, pos, pos, ())
                        else:
                            children = tuple(p.match for p in popped if p.match is not None)
                            match_start = popped[0].start_pos if popped else pos
                            match_end = popped[-1].match.end if popped and popped[-1].match else pos
                            reduced_match = Match(prod.original_op, match_start, match_end, children)

                        stack = stack + [type(stack[0])(  # noqa
                            goto_state,
                            prod.lhs,
                            reduced_match,
                            reduced_match.start,
                        )]
                        break  # Continue outer loop

                    elif isinstance(action, Accept):
                        if len(stack) >= 2 and stack[1].match is not None:
                            yield stack[1].match
                        return

                if found_action:
                    break

            if not found_action:
                return


##


def create_lr_parser(
        grammar: Grammar,
        source: str,
        **kwargs: ta.Any,
) -> _LrParser:
    """Factory function to create an LR parser instance."""

    return _LrParser(grammar, source, **kwargs)
