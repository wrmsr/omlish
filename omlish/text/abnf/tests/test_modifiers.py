"""Tests for the '%'-modifier meta-grammar extension: %token and %channel(...) on rule definition lines."""
import pytest

from .... import check
from ..errors import AbnfGrammarParseError
from ..grammars import Channel
from ..meta import parse_grammar
from ..utils import filter_match_channels
from ..utils import only_match_rules


##


def test_token_modifier():
    g = parse_grammar(
        """
        root = 1*ident
        %token ident = 1*ALPHA
        """,
        root='root',
    )

    assert not check.not_none(g.rule('root')).is_token
    assert check.not_none(g.rule('ident')).is_token

    # references are bare - the grammar parses as usual
    assert g.parse('abc', complete=True) is not None


def test_channel_modifier():
    g = parse_grammar(
        """
        root = 1*(word / WS)
        %token word = 1*ALPHA
        %channel(space) WS = 1*(SP / HTAB)
        """,
        root='root',
        no_optimize=True,
    )

    assert check.not_none(g.rule('WS')).channel is Channel.SPACE
    assert check.not_none(g.rule('word')).channel is Channel.STRUCTURE

    m = check.not_none(g.parse('ab cd', complete=True))
    m = only_match_rules(m)

    names = list(_walk_rule_names(m))
    assert 'word' in names
    assert 'WS' in names

    # channel-based filtering strips the space rules
    fm = filter_match_channels(m, g, remove=(Channel.SPACE,), keep_children=True)
    fnames = list(_walk_rule_names(fm))
    assert 'word' in fnames
    assert 'WS' not in fnames


def test_comment_channel_pickup():
    # The hot-comment use case: comment rules stay in the tree, filterable by channel.
    g = parse_grammar(
        """
        root = 1*(stmt / comment / WS)
        stmt = 1*ALPHA ";"
        %channel(comment) comment = "#" *(%x20-7E)
        %channel(space)   WS = 1*(SP / HTAB / CR / LF)
        """,
        root='root',
        no_optimize=True,
    )

    src = 'aa;# hot comment\nbb;'
    m = check.not_none(g.parse(src, complete=True))
    m = only_match_rules(m)

    comments = filter_match_channels(m, g, keep=(Channel.COMMENT,), keep_children=True)
    spans = [(c.start, c.end) for c in comments.children]
    assert spans == [(3, 16)]
    assert src[3:16] == '# hot comment'


def test_multiple_modifiers():
    g = parse_grammar(
        """
        root = 1*(word / c)
        %token word = 1*ALPHA
        %token %channel(comment) c = "#" *(%x20-7E)
        """,
        root='root',
    )

    r = check.not_none(g.rule('c'))
    assert r.is_token
    assert r.channel is Channel.COMMENT


def test_unknown_modifier():
    with pytest.raises(AbnfGrammarParseError) as ei:
        parse_grammar(
            """
            %frob root = "x"
            """,
        )

    assert 'frob' in str(ei.value)


def test_unknown_channel():
    with pytest.raises(AbnfGrammarParseError) as ei:
        parse_grammar(
            """
            %channel(nope) root = "x"
            """,
        )

    assert 'nope' in str(ei.value)


def test_duplicate_modifier():
    with pytest.raises(AbnfGrammarParseError):
        parse_grammar(
            """
            %token %token root = "x"
            """,
        )


def test_token_with_arg_rejected():
    with pytest.raises(AbnfGrammarParseError):
        parse_grammar(
            """
            %token(x) root = "x"
            """,
        )


def test_channel_without_arg_rejected():
    with pytest.raises(AbnfGrammarParseError):
        parse_grammar(
            """
            %channel root = "x"
            """,
        )


def test_modifiers_on_alt_continuation_rejected():
    with pytest.raises(AbnfGrammarParseError):
        parse_grammar(
            """
            root = "x"
            %token root =/ "y"
            """,
        )


def test_unannotated_grammar_is_plain_abnf():
    g = parse_grammar(
        """
        root = 1*DIGIT
        """,
        root='root',
    )

    r = check.not_none(g.rule('root'))
    assert not r.is_token
    assert r.channel is Channel.STRUCTURE


##


def _walk_rule_names(m):
    from ..ops import RuleRef

    if isinstance(m.op, RuleRef):
        yield m.op.name
    for c in m.children:
        yield from _walk_rule_names(c)
