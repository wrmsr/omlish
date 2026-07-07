from .. import ops
from .. import parsing


##
# Bug: casefold length change corrupts Match.end
#   CaseInsensitiveStringLiteral compares a casefolded slice but computes Match.end from the *casefolded* length.
#   str.casefold() can change length ('ß' -> 'ss'), producing Match.end past the end of the source.


def test_case_insensitive_literal_end_in_bounds() -> None:
    # 'ß'.casefold() == 'ss', so the stored value is longer than the source text.
    src = 'ß'
    m = parsing.parse(ops.CaseInsensitiveStringLiteral('ß'), src)

    # Invariant that must hold under any chosen semantics:
    assert m is None or m.end <= len(src)  # currently Match(0, 2) on a 1-char source

    # Stricter post-fix expectation, if the fix is to compare the casefolded slice but take end from the raw slice
    # length:
    # assert m is not None and (m.start, m.end) == (0, 1)


##
# Bug: repeat min-count with nullable child
#   _iter_parse_repeat's progress check (`next_max_end <= max_end_by_count[i]: break`) fires before next_matches is
#   committed, so a repetition that only matches empty never counts toward times.min. Valid parses with nullable
#   children are dropped.


def test_repeat_min_with_nullable_child() -> None:
    inner = ops.repeat(ops.StringLiteral('a'))  # *"a" -- nullable

    # 2*2(*"a") on 'a': valid as ('a', '') or ('', 'a')
    assert parsing.parse(ops.repeat(2, 2, inner), 'a') is not None

    # 1*(*"a") on '': one empty repetition
    assert parsing.parse(ops.repeat(1, None, inner), '') is not None


def test_repeat_frontier_not_pruned_by_global_max_end() -> None:
    # 3*3( "aaa" / "a" ) on 'aaa' is valid as ('a', 'a', 'a'). The old progress guard compared against the *global* max
    # end (3, via the "aaa" branch) and broke while the ('a' ...) frontier was still live at position 1.
    child = ops.either(
        ops.literal('aaa', case_sensitive=True),
        ops.literal('a', case_sensitive=True),
    )
    assert parsing.parse(ops.repeat(3, 3, child), 'aaa') is not None
