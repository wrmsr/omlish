"""
Extraction of a grammar's token-level interpretation.

Classification, driven by the '%'-modifiers in the grammar text:

- **token rules**: rules marked `%token`. Lexed by maximal munch; their bodies are inlined into self-contained
  patterns, so they must be non-recursive, non-nullable, and free of skip references. A token whose channel is SPACE or
  COMMENT is *hidden*: lexed and kept in the token stream (with exact positions - this is how comments are picked up),
  but not fed to the parser.

- **skip wrappers**: parser-level rules whose language consists entirely of hidden tokens - the conventional
  `SKIP = WS / comment`, `S = *SKIP`, `R = 1*SKIP` threading. References to them in parser rules are *elided* in token
  mode: the lexer already routed those tokens to their channels.

- **implicit literal tokens**: string literals (and single-char numeric ranges) appearing in parser rules become
  anonymous token types, ANTLR-style. They outrank named tokens on equal-length matches, which is what makes keywords
  beat identifier tokens.

- **parser rules**: everything reachable from the root that isn't the above. Their leaves must resolve to tokens,
  implicit literals, or skip wrappers - any other char-level construct is an error directing the author to wrap it in
  a `%token`.

The *adjacency check* enforces that the char-level and token-level readings of the grammar agree: wherever two tokens
can be adjacent in a parser rule, the grammar must explicitly permit skips between them (via a skip wrapper reference
on one side of the boundary or the other). Without this, token mode would silently accept whitespace the char-level
grammar rejects.
"""
import typing as ta

from ...analysis import GrammarAnalysis
from ...base import CompositeOp
from ...base import Op
from ...errors import AbnfTokenizationError
from ...grammars import Channel
from ...grammars import Grammar
from ...grammars import Rule
from ...internal import Regex
from ...ops import CaseInsensitiveStringLiteral
from ...ops import Concat
from ...ops import Either
from ...ops import RangeLiteral
from ...ops import Repeat
from ...ops import RuleRef
from ...ops import StringLiteral
from .specs import SkipKind
from .specs import TokenizedGrammar
from .specs import TokenSpec
from .specs import TokenSpecKind


##


def inline_op(
        op: Op,
        rules_by_name_f: ta.Mapping[str, Rule],
        *,
        _visiting: frozenset[str] = frozenset(),
) -> Op:
    """Recursively replaces RuleRefs with their rule bodies. Raises on recursion."""

    if isinstance(op, RuleRef):
        n = op.name_f
        if n in _visiting:
            raise AbnfTokenizationError('Recursive reference in token rule closure', rule=op.name)
        r = rules_by_name_f[n]
        return inline_op(r.op, rules_by_name_f, _visiting=_visiting | {n})

    elif isinstance(op, CompositeOp):
        return op.replace_children(*[
            inline_op(c, rules_by_name_f, _visiting=_visiting)
            for c in op.children
        ])

    else:
        return op


def _inlined_op_nullable(op: Op) -> bool:
    """Nullability of a ref-free op tree."""

    if isinstance(op, (StringLiteral, CaseInsensitiveStringLiteral, RangeLiteral)):
        return False
    elif isinstance(op, Regex):
        return op.pat.match('') is not None
    elif isinstance(op, Concat):
        return all(_inlined_op_nullable(c) for c in op.children)
    elif isinstance(op, Either):
        return any(_inlined_op_nullable(c) for c in op.children)
    elif isinstance(op, Repeat):
        return op.times.min == 0 or _inlined_op_nullable(op.child)
    else:
        raise TypeError(op)


##


class TokenExtractor:
    def __init__(
            self,
            grammar: Grammar,
            root: Rule | str | None = None,
            *,
            no_adjacency_check: bool = False,
    ) -> None:
        super().__init__()

        self._grammar = grammar
        self._root = grammar.resolve_root(root)
        self._no_adjacency_check = no_adjacency_check

        self._rules = grammar.rules.rules_by_name_f
        self._analysis = GrammarAnalysis(grammar)

        self._token_rules: dict[str, Rule] = {
            n: r
            for n, r in self._rules.items()
            if r.is_token
        }
        self._hidden_token_names: frozenset[str] = frozenset(
            n
            for n, r in self._token_rules.items()
            if r.channel in (Channel.SPACE, Channel.COMMENT)
        )

        self._skip_wrappers: dict[str, SkipKind] = self._classify_skip_wrappers()

    # skip wrappers

    def _is_skip_op(self, op: Op, wrappers: ta.Container[str]) -> bool:
        if isinstance(op, RuleRef):
            return op.name_f in self._hidden_token_names or op.name_f in wrappers
        elif isinstance(op, Repeat):
            return self._is_skip_op(op.child, wrappers)
        elif isinstance(op, (Concat, Either)):
            return all(self._is_skip_op(c, wrappers) for c in op.children)
        else:
            return False

    def _classify_skip_wrappers(self) -> dict[str, SkipKind]:
        # Greatest fixpoint: start with every non-token rule as a candidate, repeatedly remove violators.
        cands: set[str] = {
            n
            for n, r in self._rules.items()
            if not r.is_token and isinstance(r.op, (RuleRef, Repeat, Concat, Either))
        }

        while True:
            bad = {n for n in cands if not self._is_skip_op(self._rules[n].op, cands)}
            if not bad:
                break
            cands -= bad

        if self._root.name_f in cands:
            raise AbnfTokenizationError('Root rule is a skip wrapper', rule=self._root.name)

        return {
            n: SkipKind.OPTIONAL if self._analysis.op_nullable(self._rules[n].op) else SkipKind.REQUIRED
            for n in sorted(cands)
        }

    # parser-land op classification helpers

    def _ref_kind(self, op: RuleRef) -> str:
        n = op.name_f
        if n in self._skip_wrappers:
            return 'skip'
        if n in self._token_rules:
            return 'hidden-token' if n in self._hidden_token_names else 'token'
        return 'parser'

    def _op_is_skip(self, op: Op) -> bool:
        return self._is_skip_op(op, self._skip_wrappers)

    # extraction proper

    def extract(self) -> TokenizedGrammar:
        specs: list[TokenSpec] = []
        literal_specs: dict[tuple[str, bool], TokenSpec] = {}
        parser_rules: dict[str, Rule] = {}

        def add_literal(value: str, ci: bool) -> None:
            key = (value, ci)
            if key in literal_specs:
                return
            spec = TokenSpec(
                index=len(specs),
                name=f'%i"{value}"' if ci else f'"{value}"',
                kind=TokenSpecKind.LITERAL,
                literal_value=value,
                literal_case_insensitive=ci,
            )
            literal_specs[key] = spec
            specs.append(spec)

        def walk(op: Op, rule: Rule) -> None:
            if isinstance(op, RuleRef):
                k = self._ref_kind(op)
                if k == 'hidden-token':
                    raise AbnfTokenizationError(
                        f'Hidden token {op.name!r} referenced directly from a parser rule - reference it through a '
                        f'skip wrapper, or give it a non-hidden channel',
                        rule=rule.name,
                    )
                elif k == 'parser':
                    visit_rule(op.name_f)

            elif isinstance(op, StringLiteral):
                add_literal(op.value, False)

            elif isinstance(op, CaseInsensitiveStringLiteral):
                add_literal(op.value, True)

            elif isinstance(op, RangeLiteral):
                if op.value.lo != op.value.hi:
                    raise AbnfTokenizationError(
                        f'Char-level range {op.value!r} in a parser rule - wrap it in a %token rule',
                        rule=rule.name,
                    )
                add_literal(op.value.lo, False)

            elif isinstance(op, Regex):
                raise AbnfTokenizationError(
                    'Regex op in a parser rule - tokenize from an unoptimized grammar (parse_grammar(..., '
                    'no_optimize=True))',
                    rule=rule.name,
                )

            elif isinstance(op, CompositeOp):
                for c in op.children:
                    walk(c, rule)

            else:
                raise TypeError(op)

        def visit_rule(name_f: str) -> None:
            if name_f in parser_rules:
                return
            r = self._rules[name_f]
            parser_rules[name_f] = r
            walk(r.op, r)

        # Implicit literals are discovered during the parser-rule walk and take the low (high-priority) indices; token
        # rules follow in declaration order.
        visit_rule(self._root.name_f)

        token_rule_specs: dict[str, TokenSpec] = {}
        token_rule_ops: dict[str, Op] = {}
        for n, r in self._token_rules.items():
            token_rule_ops[n] = self._validate_token_rule(r)
            spec = TokenSpec(
                index=len(specs),
                name=r.name,
                kind=TokenSpecKind.RULE,
                channel=r.channel,
            )
            token_rule_specs[n] = spec
            specs.append(spec)

        if not self._no_adjacency_check:
            checker = _AdjacencyChecker(self, parser_rules)
            checker.check()

        return TokenizedGrammar(
            grammar=self._grammar,
            root=self._root,
            specs=specs,
            token_rule_specs=token_rule_specs,
            token_rule_ops=token_rule_ops,
            literal_specs=literal_specs,
            skip_wrappers=dict(self._skip_wrappers),
            parser_rules=parser_rules,
        )

    def _validate_token_rule(self, r: Rule) -> Op:
        # Raises on recursion or unresolvable refs; hidden-token / skip-wrapper refs inside tokens are fine only if
        # those rules are themselves inlinable (non-recursive), which inline_op enforces naturally.
        iop = inline_op(r.op, self._rules)

        if _inlined_op_nullable(iop):
            raise AbnfTokenizationError('Token rule may match empty - tokens must be non-nullable', rule=r.name)

        return iop


##


class _AdjacencyChecker:
    """
    Verifies that everywhere two tokens can be adjacent inside parser rules, a skip wrapper explicitly permits
    whitespace at that boundary - keeping char-level and token-level semantics aligned.

    `begins_skip` / `ends_skip` compute (as a greatest fixpoint over possibly-recursive parser rules) whether an op
    permits skip content at its very start / end when present; nullability of intervening elements drives which
    boundary pairs are possible.
    """

    def __init__(self, ext: TokenExtractor, parser_rules: ta.Mapping[str, Rule]) -> None:
        super().__init__()

        self._ext = ext
        self._parser_rules = parser_rules

        self._begins: dict[str, bool] = dict.fromkeys(parser_rules, True)
        self._ends: dict[str, bool] = dict.fromkeys(parser_rules, True)

        self._solve()

    def _nullable(self, op: Op) -> bool:
        return self._ext._analysis.op_nullable(op)  # noqa

    def _begins_skip(self, op: Op) -> bool:
        ext = self._ext
        if ext._op_is_skip(op):  # noqa
            return True

        if isinstance(op, RuleRef):
            if op.name_f in self._begins:
                return self._begins[op.name_f]
            return False  # token ref

        elif isinstance(op, Concat):
            cs = op.children
            for c in cs:
                if ext._op_is_skip(c):  # noqa
                    return True
                if not self._begins_skip(c):
                    return False
                if not self._nullable(c):
                    return True
            return True

        elif isinstance(op, Either):
            return all(self._begins_skip(c) for c in op.children)

        elif isinstance(op, Repeat):
            return self._begins_skip(op.child)

        else:
            return False

    def _ends_skip(self, op: Op) -> bool:
        ext = self._ext
        if ext._op_is_skip(op):  # noqa
            return True

        if isinstance(op, RuleRef):
            if op.name_f in self._ends:
                return self._ends[op.name_f]
            return False

        elif isinstance(op, Concat):
            for c in reversed(op.children):
                if ext._op_is_skip(c):  # noqa
                    return True
                if not self._ends_skip(c):
                    return False
                if not self._nullable(c):
                    return True
            return True

        elif isinstance(op, Either):
            return all(self._ends_skip(c) for c in op.children)

        elif isinstance(op, Repeat):
            return self._ends_skip(op.child)

        else:
            return False

    def _solve(self) -> None:
        while True:
            changed = False
            for n, r in self._parser_rules.items():
                if (b := self._begins_skip(r.op)) != self._begins[n]:
                    self._begins[n] = b
                    changed = True
                if (e := self._ends_skip(r.op)) != self._ends[n]:
                    self._ends[n] = e
                    changed = True
            if not changed:
                break

    def _check_op(self, op: Op, rule: Rule) -> None:
        ext = self._ext

        if isinstance(op, Concat):
            cs = op.children

            for j in range(1, len(cs)):
                cj = cs[j]
                if ext._op_is_skip(cj):  # noqa
                    continue

                # Walk back over possibly-absent elements to find every element cj may be adjacent to.
                for k in range(j - 1, -1, -1):
                    ck = cs[k]

                    if ext._op_is_skip(ck):  # noqa
                        # A skip element (even a nullable one, like S) explicitly permits whitespace here, for this
                        # and all earlier pairings.
                        break

                    if not (self._ends_skip(ck) or self._begins_skip(cj)):
                        raise AbnfTokenizationError(
                            f'Possibly-adjacent elements {ck} and {cj} have no skip permitted between them - add an '
                            f'S/R-style skip reference at the boundary or merge them into a %token',
                            rule=rule.name,
                        )

                    if not self._nullable(ck):
                        break

            for c in cs:
                self._check_op(c, rule)

        elif isinstance(op, Either):
            for c in op.children:
                self._check_op(c, rule)

        elif isinstance(op, Repeat):
            t = op.times
            if (t.max is None or t.max > 1) and not ext._op_is_skip(op):  # noqa
                c = op.child
                if not (self._ends_skip(c) or self._begins_skip(c)):
                    raise AbnfTokenizationError(
                        f'Repeated element {c} may be adjacent to itself with no skip permitted between repetitions',
                        rule=rule.name,
                    )
            self._check_op(op.child, rule)

    def check(self) -> None:
        for r in self._parser_rules.values():
            self._check_op(r.op, r)


##


def extract_tokenized(
        grammar: Grammar,
        root: Rule | str | None = None,
        *,
        no_adjacency_check: bool = False,
) -> TokenizedGrammar:
    return TokenExtractor(
        grammar,
        root,
        no_adjacency_check=no_adjacency_check,
    ).extract()
