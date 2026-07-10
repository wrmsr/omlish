"""Tests for token extraction (S/R elision model) and the maximal-munch lexer."""
import pytest

from ..engines.tokens import Lexer
from ..engines.tokens import SkipKind
from ..engines.tokens import TokenSpecKind
from ..engines.tokens import extract_tokenized
from ..errors import AbnfLexError
from ..errors import AbnfTokenizationError
from ..grammars import Channel
from ..meta import parse_grammar


##


_CONF_SRC = """\
single = S stmt *(S ";" S stmt) S

stmt = set-stmt / flag-stmt
set-stmt = "set" R ident S "=" S value
flag-stmt = "enable" R ident
value = ident / number / string
ident = regular-ident / "on" / "off"   ; keywords usable as identifiers

%token regular-ident = ident-start *ident-char
ident-start = ALPHA / "_"
ident-char = ALPHA / DIGIT / "_"

%token number = 1*DIGIT

%token string = squote *(string-char / squote squote) squote
squote = %x27
string-char = %x00-26 / %x28-7F

SKIP = WS / comment
S = *SKIP
R = 1*SKIP

%token %channel(space)   WS = 1*(SP / HTAB / CR / LF)
%token %channel(comment) comment = "#" *not-eol
not-eol = %x00-09 / %x0B-7F
"""


def _conf_tokenized():
    g = parse_grammar(_CONF_SRC, root='single', no_optimize=True)
    return extract_tokenized(g)


##
# extraction


def test_extraction_classification():
    tkz = _conf_tokenized()

    assert set(tkz.token_rule_specs) == {'regular-ident', 'number', 'string', 'ws', 'comment'}

    assert tkz.skip_wrappers == {
        'skip': SkipKind.REQUIRED,
        's': SkipKind.OPTIONAL,
        'r': SkipKind.REQUIRED,
    }

    assert set(tkz.parser_rules) == {'single', 'stmt', 'set-stmt', 'flag-stmt', 'value', 'ident'}

    # implicit literals, in discovery order, ahead of all token rules in priority
    lit_names = [s.name for s in tkz.specs if s.kind is TokenSpecKind.LITERAL]
    assert set(lit_names) == {'%i"set"', '%i"enable"', '%i"on"', '%i"off"', '%i"="', '%i";"'}
    max_lit = max(s.index for s in tkz.specs if s.kind is TokenSpecKind.LITERAL)
    min_rule = min(s.index for s in tkz.specs if s.kind is TokenSpecKind.RULE)
    assert max_lit < min_rule


def test_extraction_hidden_channels():
    tkz = _conf_tokenized()

    assert tkz.token_rule_specs['ws'].hidden
    assert tkz.token_rule_specs['ws'].channel is Channel.SPACE
    assert tkz.token_rule_specs['comment'].hidden
    assert tkz.token_rule_specs['comment'].channel is Channel.COMMENT
    assert not tkz.token_rule_specs['number'].hidden


def test_nullable_token_rejected():
    g = parse_grammar(
        """
        root = t
        %token t = *ALPHA
        """,
        root='root',
        no_optimize=True,
    )

    with pytest.raises(AbnfTokenizationError) as ei:
        extract_tokenized(g)
    assert 'empty' in str(ei.value)


def test_recursive_token_rejected():
    g = parse_grammar(
        """
        root = t
        %token t = "a" [t]
        """,
        root='root',
        no_optimize=True,
    )

    with pytest.raises(AbnfTokenizationError) as ei:
        extract_tokenized(g)
    assert 'ecursive' in str(ei.value)


def test_char_range_in_parser_rule_rejected():
    g = parse_grammar(
        """
        root = %x30-39
        """,
        root='root',
        no_optimize=True,
    )

    with pytest.raises(AbnfTokenizationError) as ei:
        extract_tokenized(g)
    assert '%token' in str(ei.value)


def test_single_char_range_is_implicit_literal():
    g = parse_grammar(
        """
        root = t *(S %x3B S t)
        %token t = 1*ALPHA
        S = *WS
        %token %channel(space) WS = 1*SP
        """,
        root='root',
        no_optimize=True,
    )

    tkz = extract_tokenized(g)
    assert (';', False) in tkz.literal_specs


def test_hidden_token_direct_ref_rejected():
    g = parse_grammar(
        """
        root = WS t
        %token t = 1*ALPHA
        %token %channel(space) WS = 1*SP
        """,
        root='root',
        no_optimize=True,
    )

    with pytest.raises(AbnfTokenizationError) as ei:
        extract_tokenized(g)
    assert 'idden' in str(ei.value)


##
# adjacency checking


def test_adjacent_tokens_without_skip_rejected():
    g = parse_grammar(
        """
        root = "a" "b"
        """,
        root='root',
        no_optimize=True,
    )

    with pytest.raises(AbnfTokenizationError) as ei:
        extract_tokenized(g)
    assert 'adjacent' in str(ei.value)

    extract_tokenized(g, no_adjacency_check=True)  # escape hatch


def test_adjacent_repeat_without_skip_rejected():
    g = parse_grammar(
        """
        root = 1*t
        %token t = 1*ALPHA
        """,
        root='root',
        no_optimize=True,
    )

    with pytest.raises(AbnfTokenizationError):
        extract_tokenized(g)


def test_skip_through_option_boundary_ok():
    # minisql-style: '[with-clause R] query-term' - the option's trailing R covers the present case, absence removes
    # the boundary.
    g = parse_grammar(
        """
        root = [pre R] t
        pre = "with"
        %token t = 1*ALPHA
        R = 1*WS
        %token %channel(space) WS = 1*SP
        """,
        root='root',
        no_optimize=True,
    )

    tkz = extract_tokenized(g)
    assert 'r' in tkz.skip_wrappers


def test_option_without_skip_boundary_rejected():
    g = parse_grammar(
        """
        root = [pre] t
        pre = "with"
        %token t = 1*ALPHA
        """,
        root='root',
        no_optimize=True,
    )

    with pytest.raises(AbnfTokenizationError):
        extract_tokenized(g)


##
# lexing


def test_lex_basic():
    tkz = _conf_tokenized()
    lx = Lexer(tkz)

    src = "set x = 'a''b' # note\n; enable on"
    toks = lx.lex(src)

    names = [(t.spec.name, t.text(src)) for t in toks if not t.spec.hidden]
    assert names == [
        ('%i"set"', 'set'),
        ('regular-ident', 'x'),
        ('%i"="', '='),
        ('string', "'a''b'"),
        ('%i";"', ';'),
        ('%i"enable"', 'enable'),
        ('%i"on"', 'on'),
    ]


def test_lex_maximal_munch_keywords():
    tkz = _conf_tokenized()
    lx = Lexer(tkz)

    # 'setx' munches longer as an identifier; bare 'set' ties and the implicit literal wins
    toks = lx.lex('setx')
    assert [t.spec.name for t in toks] == ['regular-ident']

    toks = lx.lex('set')
    assert [t.spec.name for t in toks] == ['%i"set"']

    # bare ABNF literals are case-insensitive
    toks = lx.lex('SET')
    assert [t.spec.name for t in toks] == ['%i"set"']


def test_lex_comment_channel_retained():
    tkz = _conf_tokenized()
    lx = Lexer(tkz)

    src = 'x # hot comment\ny'
    toks = lx.lex(src)

    comments = [t for t in toks if t.spec.channel is Channel.COMMENT]
    assert [t.text(src) for t in comments] == ['# hot comment']


def test_lex_numbers_and_idents():
    tkz = _conf_tokenized()
    lx = Lexer(tkz)

    src = 'set _a1 = 42'
    toks = [t for t in lx.lex(src) if not t.spec.hidden]
    assert [(t.spec.name, t.text(src)) for t in toks] == [
        ('%i"set"', 'set'),
        ('regular-ident', '_a1'),
        ('%i"="', '='),
        ('number', '42'),
    ]


def test_lex_error_position():
    tkz = _conf_tokenized()
    lx = Lexer(tkz)

    with pytest.raises(AbnfLexError) as ei:
        lx.lex('set x = \x01')

    assert ei.value.offset == 8
    assert 'line 1' in str(ei.value)


def test_lex_interp_fallback_string():
    # The quoted-string token (with '' escaping) is not provably regex-longest-safe, so it exercises the interp
    # fallback path.
    tkz = _conf_tokenized()
    lx = Lexer(tkz)

    src = "'it''s'"
    toks = lx.lex(src)
    assert [(t.spec.name, t.text(src)) for t in toks] == [('string', "'it''s'")]
