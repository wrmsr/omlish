from .... import check
from .. import internal
from .. import meta
from .. import ops
from .. import opto
from ..grammars import Grammar
from ..grammars import Rule


# def test_optimize_literal():
#     """Test that a simple literal is converted to Regex."""
#
#     op = ops.StringLiteral('hello')
#     optimized = opto.optimize_op(op)
#     assert isinstance(optimized, internal.Regex)
#     assert optimized.pat.pattern == r'hello'
#
#
# def test_optimize_case_insensitive_literal():
#     """Test that a case-insensitive literal is converted to Regex."""
#
#     op = ops.CaseInsensitiveStringLiteral('hello')
#     optimized = opto.optimize_op(op)
#     assert isinstance(optimized, internal.Regex)
#     assert optimized.pat.pattern == r'(?i:hello)'
#
#
# def test_optimize_range_literal():
#     """Test that a range literal is converted to Regex."""
#
#     op = ops.RangeLiteral(ops.RangeLiteral.Range('a', 'z'))
#     optimized = opto.optimize_op(op)
#     assert isinstance(optimized, internal.Regex)
#     assert optimized.pat.pattern == '[a-z]'
#
#
# def test_optimize_concat():
#     """Test that a concat of literals is converted to a single Regex."""
#
#     op = ops.concat(
#         ops.StringLiteral('hello'),
#         ops.StringLiteral(' '),
#         ops.StringLiteral('world'),
#     )
#     optimized = opto.optimize_op(op)
#     assert isinstance(optimized, internal.Regex)
#     assert optimized.pat.pattern == r'hello\ world'
#
#
# def test_optimize_repeat():
#     """Test that a repeat of a literal is converted to Regex."""
#
#     # Test various repeat patterns
#     op1 = ops.Repeat(ops.Repeat.Times(0, None), ops.StringLiteral('a'))
#     optimized1 = opto.optimize_op(op1)
#     assert isinstance(optimized1, internal.Regex)
#     assert optimized1.pat.pattern == 'a*'
#
#     op2 = ops.Repeat(ops.Repeat.Times(1, None), ops.StringLiteral('a'))
#     optimized2 = opto.optimize_op(op2)
#     assert isinstance(optimized2, internal.Regex)
#     assert optimized2.pat.pattern == 'a+'
#
#     op3 = ops.Repeat(ops.Repeat.Times(0, 1), ops.StringLiteral('a'))
#     optimized3 = opto.optimize_op(op3)
#     assert isinstance(optimized3, internal.Regex)
#     assert optimized3.pat.pattern == 'a?'
#
#     op4 = ops.Repeat(ops.Repeat.Times(3, 5), ops.StringLiteral('a'))
#     optimized4 = opto.optimize_op(op4)
#     assert isinstance(optimized4, internal.Regex)
#     assert optimized4.pat.pattern == 'a{3,5}'
#
#
# def test_optimize_repeat_complex():
#     """Test that a repeat of a concat is converted to Regex with proper grouping."""
#
#     op = ops.Repeat(
#         ops.Repeat.Times(0, None),
#         ops.concat(
#             ops.StringLiteral('ab'),
#             ops.StringLiteral('cd'),
#         ),
#     )
#     optimized = opto.optimize_op(op)
#     assert isinstance(optimized, internal.Regex)
#     # Should wrap the concat pattern in a non-capturing group
#     assert optimized.pat.pattern == '(?:abcd)*'
#
#
# def test_optimize_either_first_match():
#     """Test that Either with first_match=True is converted to Regex."""
#
#     op = ops.Either(
#         ops.StringLiteral('cat'),
#         ops.StringLiteral('dog'),
#         ops.StringLiteral('bird'),
#         first_match=True,
#     )
#     optimized = opto.optimize_op(op)
#     assert isinstance(optimized, internal.Regex)
#     assert optimized.pat.pattern == '(cat|dog|bird)'
#
#
# def test_optimize_either_longest_match():
#     """Test that Either with first_match=False is NOT converted to a single Regex."""
#
#     op = ops.Either(
#         ops.StringLiteral('cat'),
#         ops.StringLiteral('dog'),
#         first_match=False,
#     )
#     optimized = opto.optimize_op(op)
#     # Should not be converted to a single Regex because longest-match semantics differ from regex
#     assert isinstance(optimized, ops.Either)
#     # But the children should be optimized to Regex ops
#     assert isinstance(optimized.children[0], internal.Regex)
#     assert isinstance(optimized.children[1], internal.Regex)
#     assert optimized.first_match is False
#
#
# def test_optimize_rule_ref_barrier():
#     """Test that RuleRef acts as an optimization barrier."""
#
#     op = ops.RuleRef('some-rule')
#     optimized = opto.optimize_op(op)
#     # RuleRef should not be converted
#     assert isinstance(optimized, ops.RuleRef)
#     assert optimized is op  # Should return the original op
#
#
# def test_optimize_concat_with_rule_ref():
#     """Test that a concat containing a RuleRef is partially optimized."""
#
#     op = ops.concat(
#         ops.StringLiteral('prefix'),
#         ops.RuleRef('some-rule'),
#         ops.StringLiteral('suffix'),
#     )
#     optimized = opto.optimize_op(op)
#     # Should still be a Concat, but prefix and suffix should be optimized
#     assert isinstance(optimized, ops.Concat)
#     assert len(optimized.children) == 3
#     assert isinstance(optimized.children[0], internal.Regex)
#     assert isinstance(optimized.children[1], ops.RuleRef)
#     assert isinstance(optimized.children[2], internal.Regex)
#
#
# def test_optimize_no_change():
#     """Test that if no optimization is possible, the original op is returned."""
#
#     op = ops.RuleRef('some-rule')
#     optimized = opto.optimize_op(op)
#     assert optimized is op
#
#
# def test_optimize_already_regex():
#     """Test that an existing Regex op is returned unchanged."""
#
#     import re
#     op = internal.Regex(re.compile(r'test'))
#     optimized = opto.optimize_op(op)
#     assert optimized is op
#
#
# def test_optimize_nested():
#     """Test a complex nested structure."""
#
#     op = ops.concat(
#         ops.Repeat(
#             ops.Repeat.Times(1, None),
#             ops.RangeLiteral(ops.RangeLiteral.Range('a', 'z')),
#         ),
#         ops.StringLiteral(':'),
#         ops.Repeat(
#             ops.Repeat.Times(0, None),
#             ops.RangeLiteral(ops.RangeLiteral.Range('0', '9')),
#         ),
#     )
#     optimized = opto.optimize_op(op)
#     # The entire thing should be converted to a single Regex
#     assert isinstance(optimized, internal.Regex)
#     assert optimized.pat.pattern == '[a-z]+:[0-9]*'
#
#
# def test_optimization_preserves_semantics():
#     """Test that optimization preserves matching semantics."""
#
#     from ..parsing import parse
#
#     # Create an op and its optimized version
#     op = ops.concat(
#         ops.Repeat(
#             ops.Repeat.Times(1, None),
#             ops.CaseInsensitiveStringLiteral('ab'),
#         ),
#         ops.StringLiteral('cd'),
#     )
#     optimized = opto.optimize_op(op)
#
#     # Both should match the same strings
#     test_str = 'AbaBabcd'
#
#     match1 = parse(op, test_str)
#     match2 = parse(optimized, test_str)
#
#     assert match1 is not None
#     assert match2 is not None
#     assert match1.start == match2.start
#     assert match1.end == match2.end


##
# Bug: greedy regex conversion breaks backtracking
#   optimize_grammar converts Repeat-over-regexable subtrees (e.g. 1*%x30-39) into a single greedy re.Pattern.
#   _iter_parse_regex yields exactly one match, so the shorter alternatives the interpreted Repeat would yield are gone
#   and cross-rule backtracking fails. parse_grammar applies this by default.


def test_optimize_preserves_repeat_backtracking() -> None:
    # N = 1*%x30-39 ; root = N %x30-39
    g = Grammar(
        Rule('N', ops.repeat(1, ops.literal('0', '9'))),
        Rule('root', ops.concat(ops.rule('N'), ops.literal('0', '9'))),
        root='root',
    )

    assert g.parse('12') is not None  # interpreted: N='1', then '2'

    og = opto.optimize_grammar(g)
    # N is now Regex('[0-9]+'): eats '12' greedily, yields only that one match, and the trailing %x30-39 has nothing
    # left.
    assert og.parse('12') is not None


def test_parse_grammar_default_optimize_backtracking() -> None:
    # End-to-end: parse_grammar optimizes by default. Inline %x ranges (common in real RFC grammars) are exactly what
    # triggers the Repeat->Regex conversion.
    g = meta.parse_grammar(
        """
        root = num %x30-39
        num  = 1*%x30-39
        """,
        root='root',
    )

    assert g.parse('12') is not None


def test_optimized_matches_are_superset_of_raw() -> None:
    # Invariant: optimization must not remove parses.
    g = Grammar(
        Rule('N', ops.repeat(1, ops.literal('0', '9'))),
        root='N',
    )

    raw = {(m.start, m.end) for m in g.iter_parse('123')}          # {(0,1), (0,2), (0,3)}
    opt = {(m.start, m.end) for m in opto.optimize_grammar(g).iter_parse('123')}  # {(0,3)}

    assert raw <= opt


##
# parse_only optimization level: FIRST/FOLLOW-analysis-gated greedy conversion. Contract: preserves Grammar.parse()
# (longest match from root), not the full iter_parse() multiset.


def test_parse_only_converts_delimited_repeat():
    # N's follow set is {';'}, disjoint from its extension chars {0-9} - safe to convert greedily.
    g = Grammar(
        Rule('root', ops.concat(ops.rule('N'), ops.literal(';'))),
        Rule('N', ops.repeat(1, ops.literal('0', '9'))),
        root='root',
    )

    og = opto.optimize_grammar(g, parse_only=True)

    assert isinstance(check.not_none(og.rule('N')).op, internal.Regex)

    m = og.parse('123;')
    assert m is not None
    assert (m.start, m.end) == (0, 4)


def test_parse_only_refuses_overlapping_follow():
    # N followed by another digit: FOLLOW(N) intersects EXTEND(N), so greedy conversion would break the parse.
    g = Grammar(
        Rule('root', ops.concat(ops.rule('N'), ops.literal('0', '9'))),
        Rule('N', ops.repeat(1, ops.literal('0', '9'))),
        root='root',
    )

    og = opto.optimize_grammar(g, parse_only=True)

    assert not isinstance(check.not_none(og.rule('N')).op, internal.Regex)
    assert og.parse('12') is not None


def test_parse_only_root_conversion_loses_short_matches():
    # A bare 1*DIGIT root has empty FOLLOW, so it converts - parse() is preserved but iter_parse loses the shorter
    # alternatives. This is the documented parse_only contract.
    g = Grammar(
        Rule('N', ops.repeat(1, ops.literal('0', '9'))),
        root='N',
    )

    raw = {(m.start, m.end) for m in g.iter_parse('123')}
    assert raw == {(0, 1), (0, 2), (0, 3)}

    og = opto.optimize_grammar(g, parse_only=True)
    opt = {(m.start, m.end) for m in og.iter_parse('123')}
    assert opt == {(0, 3)}

    m = og.parse('123')
    assert m is not None
    assert (m.start, m.end) == (0, 3)


def test_parse_only_recursive_grammar_terminates():
    # op_extend must not infinitely recurse through rule cycles.
    g = meta.parse_grammar(
        """
        value = "[" value "]" / "x"
        """,
        root='value',
        no_optimize=True,
    )

    og = opto.optimize_grammar(g, parse_only=True)

    assert og.parse('[[x]]', complete=True) is not None


def test_first_match_either_converts_to_atomic_group():
    # Committed choice must stay committed through regex conversion: interpreted first_match commits to branch "a",
    # then fails on "c" vs "b". A plain regex alternation would backtrack into "ab" and wrongly succeed.
    g = Grammar(
        Rule('root', ops.concat(
            ops.either(
                ops.literal('a', case_sensitive=True),
                ops.literal('ab', case_sensitive=True),
                first_match=True,
            ),
            ops.literal('c', case_sensitive=True),
        )),
        root='root',
    )

    assert g.parse('abc', complete=False) is None

    og = opto.optimize_grammar(g, parse_only=True)
    root_op = check.not_none(og.rule('root')).op
    assert isinstance(root_op, internal.Regex)
    assert '(?>' in root_op.pat.pattern

    assert og.parse('abc', complete=False) is None
    assert og.parse('ac', complete=False) is not None
