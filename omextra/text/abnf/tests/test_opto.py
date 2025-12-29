from .. import internal
from .. import ops
from .. import opto


def test_optimize_literal():
    """Test that a simple literal is converted to Regex."""

    op = ops.StringLiteral('hello')
    optimized = opto.optimize_op(op)
    assert isinstance(optimized, internal.Regex)
    assert optimized.pat.pattern == r'hello'


def test_optimize_case_insensitive_literal():
    """Test that a case-insensitive literal is converted to Regex."""

    op = ops.CaseInsensitiveStringLiteral('hello')
    optimized = opto.optimize_op(op)
    assert isinstance(optimized, internal.Regex)
    assert optimized.pat.pattern == r'(?i:hello)'


def test_optimize_range_literal():
    """Test that a range literal is converted to Regex."""

    op = ops.RangeLiteral(ops.RangeLiteral.Range('a', 'z'))
    optimized = opto.optimize_op(op)
    assert isinstance(optimized, internal.Regex)
    assert optimized.pat.pattern == '[a-z]'


def test_optimize_concat():
    """Test that a concat of literals is converted to a single Regex."""

    op = ops.Concat(
        ops.StringLiteral('hello'),
        ops.StringLiteral(' '),
        ops.StringLiteral('world'),
    )
    optimized = opto.optimize_op(op)
    assert isinstance(optimized, internal.Regex)
    assert optimized.pat.pattern == r'hello\ world'


def test_optimize_repeat():
    """Test that a repeat of a literal is converted to Regex."""

    # Test various repeat patterns
    op1 = ops.Repeat(ops.Repeat.Times(0, None), ops.StringLiteral('a'))
    optimized1 = opto.optimize_op(op1)
    assert isinstance(optimized1, internal.Regex)
    assert optimized1.pat.pattern == 'a*'

    op2 = ops.Repeat(ops.Repeat.Times(1, None), ops.StringLiteral('a'))
    optimized2 = opto.optimize_op(op2)
    assert isinstance(optimized2, internal.Regex)
    assert optimized2.pat.pattern == 'a+'

    op3 = ops.Repeat(ops.Repeat.Times(0, 1), ops.StringLiteral('a'))
    optimized3 = opto.optimize_op(op3)
    assert isinstance(optimized3, internal.Regex)
    assert optimized3.pat.pattern == 'a?'

    op4 = ops.Repeat(ops.Repeat.Times(3, 5), ops.StringLiteral('a'))
    optimized4 = opto.optimize_op(op4)
    assert isinstance(optimized4, internal.Regex)
    assert optimized4.pat.pattern == 'a{3,5}'


def test_optimize_repeat_complex():
    """Test that a repeat of a concat is converted to Regex with proper grouping."""

    op = ops.Repeat(
        ops.Repeat.Times(0, None),
        ops.Concat(
            ops.StringLiteral('ab'),
            ops.StringLiteral('cd'),
        ),
    )
    optimized = opto.optimize_op(op)
    assert isinstance(optimized, internal.Regex)
    # Should wrap the concat pattern in a non-capturing group
    assert optimized.pat.pattern == '(?:abcd)*'


def test_optimize_either_first_match():
    """Test that Either with first_match=True is converted to Regex."""

    op = ops.Either(
        ops.StringLiteral('cat'),
        ops.StringLiteral('dog'),
        ops.StringLiteral('bird'),
        first_match=True,
    )
    optimized = opto.optimize_op(op)
    assert isinstance(optimized, internal.Regex)
    assert optimized.pat.pattern == '(cat|dog|bird)'


def test_optimize_either_longest_match():
    """Test that Either with first_match=False is NOT converted to a single Regex."""

    op = ops.Either(
        ops.StringLiteral('cat'),
        ops.StringLiteral('dog'),
        first_match=False,
    )
    optimized = opto.optimize_op(op)
    # Should not be converted to a single Regex because longest-match semantics differ from regex
    assert isinstance(optimized, ops.Either)
    # But the children should be optimized to Regex ops
    assert isinstance(optimized.children[0], internal.Regex)
    assert isinstance(optimized.children[1], internal.Regex)
    assert optimized.first_match is False


def test_optimize_rule_ref_barrier():
    """Test that RuleRef acts as an optimization barrier."""

    op = ops.RuleRef('some-rule')
    optimized = opto.optimize_op(op)
    # RuleRef should not be converted
    assert isinstance(optimized, ops.RuleRef)
    assert optimized is op  # Should return the original op


def test_optimize_concat_with_rule_ref():
    """Test that a concat containing a RuleRef is partially optimized."""

    op = ops.Concat(
        ops.StringLiteral('prefix'),
        ops.RuleRef('some-rule'),
        ops.StringLiteral('suffix'),
    )
    optimized = opto.optimize_op(op)
    # Should still be a Concat, but prefix and suffix should be optimized
    assert isinstance(optimized, ops.Concat)
    assert len(optimized.children) == 3
    assert isinstance(optimized.children[0], internal.Regex)
    assert isinstance(optimized.children[1], ops.RuleRef)
    assert isinstance(optimized.children[2], internal.Regex)


def test_optimize_no_change():
    """Test that if no optimization is possible, the original op is returned."""

    op = ops.RuleRef('some-rule')
    optimized = opto.optimize_op(op)
    assert optimized is op


def test_optimize_already_regex():
    """Test that an existing Regex op is returned unchanged."""

    import re
    op = internal.Regex(re.compile(r'test'))
    optimized = opto.optimize_op(op)
    assert optimized is op


def test_optimize_nested():
    """Test a complex nested structure."""

    op = ops.Concat(
        ops.Repeat(
            ops.Repeat.Times(1, None),
            ops.RangeLiteral(ops.RangeLiteral.Range('a', 'z')),
        ),
        ops.StringLiteral(':'),
        ops.Repeat(
            ops.Repeat.Times(0, None),
            ops.RangeLiteral(ops.RangeLiteral.Range('0', '9')),
        ),
    )
    optimized = opto.optimize_op(op)
    # The entire thing should be converted to a single Regex
    assert isinstance(optimized, internal.Regex)
    assert optimized.pat.pattern == '[a-z]+:[0-9]*'


def test_optimization_preserves_semantics():
    """Test that optimization preserves matching semantics."""

    from ..parsing import parse

    # Create an op and its optimized version
    op = ops.Concat(
        ops.Repeat(
            ops.Repeat.Times(1, None),
            ops.CaseInsensitiveStringLiteral('ab'),
        ),
        ops.StringLiteral('cd'),
    )
    optimized = opto.optimize_op(op)

    # Both should match the same strings
    test_str = 'AbaBabcd'

    match1 = parse(op, test_str)
    match2 = parse(optimized, test_str)

    assert match1 is not None
    assert match2 is not None
    assert match1.start == match2.start
    assert match1.end == match2.end
