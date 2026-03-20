# Copyright (c) 2016, Daniel Martí. All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the
# following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this list of conditions and the following
#   disclaimer.
# * Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following
#   disclaimer in the documentation and/or other materials provided with the distribution.
# * Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote
#   products derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
# INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
r"""
TODO: original go for higher-level IO/initialization functions:

type ParserOption func(*Parser)

func KeepComments(enabled bool) ParserOption { ... }
func Variant(l LangVariant) ParserOption { ... }
func StopAt(word string) ParserOption { ... }
func RecoverErrors(maximum int) ParserOption { ... }
func NewParser(options ...ParserOption) *Parser { ... }
func (p *Parser) Parse(r io.Reader, name string) (*File, error) { ... }
func (p *Parser) Stmts(r io.Reader, fn func(*Stmt) bool) error { ... }
func (p *Parser) StmtsSeq(r io.Reader) iter.Seq2[*Stmt, error] { ... }
type wrappedReader struct { ... }
func (p *Parser) Interactive(r io.Reader, fn func([]*Stmt) bool) error { ... }
func (p *Parser) InteractiveSeq(r io.Reader) iter.Seq2[[]*Stmt, error] { ... }
func (p *Parser) Words(r io.Reader, fn func(*Word) bool) error { ... }
func (p *Parser) WordsSeq(r io.Reader) iter.Seq2[*Word, error] { ... }
func (p *Parser) Document(r io.Reader) (*Word, error) { ... }
func (p *Parser) Arithmetic(r io.Reader) (ArithmExpr, error) { ... }

type ParseError struct { Filename, Pos, Text, Incomplete }
type LangError struct { Filename, Pos, Feature, Langs, LangUsed }
"""  # noqa
import typing as ta

from .langs import LANG_BASH_LIKE
from .langs import LANG_BATS
from .langs import LANG_MIR_BSD_KORN
from .langs import LANG_POSIX
from .langs import LANG_ZSH
from .langs import LangVariant
from .langs import lang_bits
from .langs import lang_in
from .lexer import _EOF_RUNE
from .lexer import _ESC_NEWL
from .lexer import ascii_digit
from .lexer import ascii_letter
from .lexer import param_name_rune
from .lexer import single_rune_param
from .lexer import test_binary_op
from .nodes import RECOVERED_POS
from .nodes import ArithmCmd
from .nodes import ArithmExp
from .nodes import ArrayElem
from .nodes import ArrayExpr
from .nodes import Assign
from .nodes import BinaryCmd
from .nodes import BinaryTest
from .nodes import Block
from .nodes import CallExpr
from .nodes import CaseClause
from .nodes import CaseItem
from .nodes import CmdSubst
from .nodes import Comment
from .nodes import CoprocClause
from .nodes import CStyleLoop
from .nodes import DblQuoted
from .nodes import DeclClause
from .nodes import Expansion
from .nodes import ExtGlob
from .nodes import File
from .nodes import FlagsArithm
from .nodes import ForClause
from .nodes import FuncDecl
from .nodes import IfClause
from .nodes import LetClause
from .nodes import Lit
from .nodes import Node
from .nodes import ParamExp
from .nodes import ParenTest
from .nodes import Pos
from .nodes import ProcSubst
from .nodes import Redirect
from .nodes import Replace
from .nodes import SglQuoted
from .nodes import Slice
from .nodes import Stmt
from .nodes import Subshell
from .nodes import TestClause
from .nodes import TestDecl
from .nodes import TestExpr
from .nodes import TimeClause
from .nodes import UnaryTest
from .nodes import WhileClause
from .nodes import Word
from .nodes import WordIter
from .nodes import WordPart
from .nodes import new_pos
from .nodes import pos_add_col
from .tokens import BinCmdOperator
from .tokens import BinTestOperator
from .tokens import CaseOperator
from .tokens import GlobOperator
from .tokens import ParExpOperator
from .tokens import ParNamesOperator
from .tokens import ProcOperator
from .tokens import RedirOperator
from .tokens import Token
from .tokens import UnTestOperator


##


# Quote state constants
_NO_STATE = 1 << 0
_RUNE_BY_RUNE = 1 << 1
_UNQUOTED_WORD_CONT = 1 << 2
_SUB_CMD = 1 << 3
_SUB_CMD_BCKQUO = 1 << 4
_DBL_QUOTES = 1 << 5
_HDOC_WORD = 1 << 6
_HDOC_BODY = 1 << 7
_HDOC_BODY_TABS = 1 << 8
_ARITHM_EXPR = 1 << 9
_ARITHM_EXPR_LET = 1 << 10
_ARITHM_EXPR_CMD = 1 << 11
_TEST_EXPR = 1 << 12
_TEST_EXPR_REGEXP = 1 << 13
_SWITCH_CASE = 1 << 14
_PARAM_EXP_ARITHM = 1 << 15
_PARAM_EXP_REPL = 1 << 16
_PARAM_EXP_EXP = 1 << 17
_ARRAY_ELEMS = 1 << 18

_ALL_KEEP_SPACES = _RUNE_BY_RUNE | _PARAM_EXP_REPL | _DBL_QUOTES | _HDOC_BODY | _HDOC_BODY_TABS | _PARAM_EXP_EXP
_ALL_REG_TOKENS = _NO_STATE | _UNQUOTED_WORD_CONT | _SUB_CMD | _SUB_CMD_BCKQUO | _HDOC_WORD | _SWITCH_CASE | _ARRAY_ELEMS | _TEST_EXPR  # noqa
_ALL_ARITHM_EXPR = _ARITHM_EXPR | _ARITHM_EXPR_LET | _ARITHM_EXPR_CMD | _PARAM_EXP_ARITHM
_ALL_PARAM_EXP = _PARAM_EXP_ARITHM | _PARAM_EXP_REPL | _PARAM_EXP_EXP

_RECOVERED_POS = RECOVERED_POS


class _SaveState(ta.NamedTuple):
    quote: int
    buried_hdocs: int


##


# IsKeyword returns True if the given word is a language keyword
# in POSIX Shell or Bash.
def is_keyword(word: str) -> bool:
    # This list has been copied from the bash 5.1 source code, file y.tab.c +4460
    if word in (
        '!',
        '[[',  # only if COND_COMMAND is defined
        ']]',  # only if COND_COMMAND is defined
        'case',
        'coproc',  # only if COPROCESS_SUPPORT is defined
        'do',
        'done',
        'else',
        'esac',
        'fi',
        'for',
        'function',
        'if',
        'in',
        'select',  # only if SELECT_COMMAND is defined
        'then',
        'time',  # only if COMMAND_TIMING is defined
        'until',
        'while',
        '{',
        '}',
    ):
        return True
    return False


# ValidName returns whether val is a valid name as per the POSIX spec.
def valid_name(val: str) -> bool:
    if val == '':
        return False
    for i, r in enumerate(val):
        if ascii_letter(r) or r == '_':
            pass
        elif i > 0 and ascii_digit(r):
            pass
        else:
            return False
    return True


def number_literal(val: str) -> bool:
    if len(val) == 0:
        return False
    for r in val:
        if not ascii_digit(r):
            return False
    return True


##


class Parser:
    """Parser holds the internal state of the parsing mechanism of a program."""

    # Expose quote state constants as class attributes for access from other modules
    _NO_STATE = _NO_STATE
    _RUNE_BY_RUNE = _RUNE_BY_RUNE
    _UNQUOTED_WORD_CONT = _UNQUOTED_WORD_CONT
    _SUB_CMD = _SUB_CMD
    _SUB_CMD_BCKQUO = _SUB_CMD_BCKQUO
    _DBL_QUOTES = _DBL_QUOTES
    _HDOC_WORD = _HDOC_WORD
    _HDOC_BODY = _HDOC_BODY
    _HDOC_BODY_TABS = _HDOC_BODY_TABS
    _ARITHM_EXPR = _ARITHM_EXPR
    _ARITHM_EXPR_LET = _ARITHM_EXPR_LET
    _ARITHM_EXPR_CMD = _ARITHM_EXPR_CMD
    _TEST_EXPR = _TEST_EXPR
    _TEST_EXPR_REGEXP = _TEST_EXPR_REGEXP
    _SWITCH_CASE = _SWITCH_CASE
    _PARAM_EXP_ARITHM = _PARAM_EXP_ARITHM
    _PARAM_EXP_REPL = _PARAM_EXP_REPL
    _PARAM_EXP_EXP = _PARAM_EXP_EXP
    _ARRAY_ELEMS = _ARRAY_ELEMS
    _ALL_KEEP_SPACES = _ALL_KEEP_SPACES
    _ALL_REG_TOKENS = _ALL_REG_TOKENS
    _ALL_ARITHM_EXPR = _ALL_ARITHM_EXPR
    _ALL_PARAM_EXP = _ALL_PARAM_EXP
    _RECOVERED_POS = _RECOVERED_POS

    def __init__(self) -> None:
        super().__init__()

        self.src: str = ''
        self.bsp: int = 0
        self.r: str = ''
        self.w: int = 0

        self.f: File | None = None

        self.spaced: bool = False

        self.err: Exception | None = None
        self.read_err: Exception | None = None
        self.read_eof: bool = False

        self.tok: Token = Token.ILLEGAL_TOK
        self.val: str = ''

        self.offs: int = 0
        self.line: int = 1
        self.col: int = 1

        self.pos: Pos = Pos()

        self.quote: int = _NO_STATE
        self.eql_offs: int = 0

        self.keep_comments: bool = False
        self.lang: LangVariant = LangVariant(0)

        self.stop_at: str | None = None

        self.recovered_errors: int = 0
        self.recover_errors_max: int = 0

        self.forbid_nested: bool = False

        self.buried_hdocs: int = 0
        self.heredocs: list[Redirect] = []

        self.hdoc_stops: list[str | None] = []

        self.parsing_doc: bool = False

        self.open_nodes: int = 0
        self.open_bquotes: int = 0

        self.last_bquote_esc: int = 0

        self.rx_open_parens: int = 0
        self.rx_first_part: bool = False

        self.acc_coms: list[Comment] = []
        self.cur_coms: list[Comment] = []

        self.lit_bs: list[str] | None = None

    # -- Lexer methods (delegated to lexer.py functions) --

    def rune(self) -> str:
        """Advance to next character in source. Returns the new p.r."""

        if self.r == '\n' or self.r == _ESC_NEWL:
            self.line += 1
            self.col = 0
        self.col += self.w

        bquotes = 0

        while True:  # retry loop
            if self.bsp >= len(self.src):
                self.bsp = len(self.src) + 1
                self.r = _EOF_RUNE
                self.w = 1
                return self.r

            b = self.src[self.bsp]
            self.bsp += 1

            if b == '\x00':
                # Ignore null bytes while parsing, like bash.
                self.col += 1
                continue

            if b == '\r':
                if self.peek() == '\n':  # \r\n turns into \n
                    self.col += 1
                    continue

            if b == '\\':
                if self.r != '\\':
                    if self.peek() == '\n':
                        self.bsp += 1
                        self.w, self.r = 1, _ESC_NEWL
                        return _ESC_NEWL
                    p1, p2 = self.peek_two()
                    if p1 == '\r' and p2 == '\n':  # \\\r\n turns into \\\n
                        self.col += 1
                        self.bsp += 2
                        self.w, self.r = 2, _ESC_NEWL
                        return _ESC_NEWL

                self.read_eof = False
                if (
                    self.open_bquotes > 0
                    and bquotes < self.open_bquotes
                    and self.bsp < len(self.src)
                    and self.src[self.bsp] in ('$', '`', '\\')
                ):
                    bquotes += 1
                    self.col += 1
                    continue

            if b == '`':
                self.last_bquote_esc = bquotes
            if self.lit_bs is not None:
                self.lit_bs.append(b)
            self.w, self.r = 1, b
            return self.r

    def peek(self) -> str:
        if self.bsp >= len(self.src):
            return _EOF_RUNE
        return self.src[self.bsp]

    def peek_two(self) -> tuple[str, str]:
        if self.bsp >= len(self.src):
            return _EOF_RUNE, _EOF_RUNE
        if self.bsp + 1 >= len(self.src):
            return self.src[self.bsp], _EOF_RUNE
        return self.src[self.bsp], self.src[self.bsp + 1]

    def next(self) -> None:
        from .lexer import next_
        next_(self)

    def next_pos(self) -> Pos:
        offset = min(self.offs + self.bsp - self.w, 0x7fffffff)
        return new_pos(offset, self.line, self.col)

    def _comment(self, hash_pos: Pos, text: str) -> Comment:
        return Comment(hash=hash_pos, text=text)

    # -- Parser helper methods --

    def lit(self, pos: Pos, val: str) -> Lit:
        l = Lit(value_pos=pos, value_end=self.next_pos(), value=val)
        return l

    def word_any_number(self) -> Word:
        w = Word()
        w.parts = self.word_parts([])
        return w

    def word_one(self, part: WordPart) -> Word:
        w = Word(parts=[part])
        return w

    def call(self, w: Word | None) -> CallExpr:
        ce = CallExpr()
        if w is not None:
            ce.args = [w]
        else:
            ce.args = []
        return ce

    def pre_nested(self, quote: int) -> _SaveState:
        s = _SaveState(quote=self.quote, buried_hdocs=self.buried_hdocs)
        self.buried_hdocs, self.quote = len(self.heredocs), quote
        return s

    def post_nested(self, s: _SaveState) -> None:
        self.quote, self.buried_hdocs = s.quote, s.buried_hdocs

    def unquoted_word_bytes(self, w: Word) -> tuple[str, bool]:
        buf: list[str] = []
        did_unquote = False
        for wp in w.parts:
            buf, did_unquote = self._unquoted_word_part(buf, wp, False)
        return ''.join(buf), did_unquote

    def _unquoted_word_part(
            self, buf: list[str], wp: WordPart, quotes: bool,
    ) -> tuple[list[str], bool]:
        quoted = False
        if isinstance(wp, Lit):
            i = 0
            while i < len(wp.value):
                b = wp.value[i]
                if b == '\\' and not quotes:
                    i += 1
                    if i < len(wp.value):
                        buf.append(wp.value[i])
                    quoted = True
                else:
                    buf.append(b)
                i += 1
        elif isinstance(wp, SglQuoted):
            buf.extend(wp.value)
            quoted = True
        elif isinstance(wp, DblQuoted):
            for wp2 in wp.parts:
                buf, _ = self._unquoted_word_part(buf, wp2, True)
            quoted = True
        return buf, quoted

    def do_heredocs(self) -> None:
        hdocs = self.heredocs[self.buried_hdocs:]
        if len(hdocs) == 0:
            return
        self.rune()  # consume '\n', since we know p.tok == Token.NEWL_
        old = self.quote
        self.heredocs = self.heredocs[:self.buried_hdocs]
        for i, r in enumerate(hdocs):
            if self.err is not None:
                break
            self.quote = _HDOC_BODY
            if r.op == RedirOperator.DASH_HDOC:
                self.quote = _HDOC_BODY_TABS
            stop, quoted = self.unquoted_word_bytes(r.word)
            self.hdoc_stops.append(stop)
            if i > 0 and self.r == '\n':
                self.rune()
            if quoted:
                from .lexer import quoted_hdoc_word
                r.hdoc = quoted_hdoc_word(self)
            else:
                self.next()
                r.hdoc = self.get_word()
            stop2 = self.hdoc_stops[-1]
            if stop2 is not None:
                self.pos_err(r.pos(), 'unclosed here-document %s', stop2)
            self.hdoc_stops.pop()
        self.quote = old

    def got(self, tok: Token) -> bool:
        if self.tok == tok:
            self.next()
            return True
        return False

    def got_rsrv(self, val: str) -> tuple[Pos, bool]:
        pos = self.pos
        if self.tok == Token.LIT_WORD_ and self.val == val:
            self.next()
            return pos, True
        return pos, False

    def recover_error(self) -> bool:
        if self.recovered_errors < self.recover_errors_max:
            self.recovered_errors += 1
            return True
        return False

    def follow_err(self, pos: Pos, left: ta.Any, right: ta.Any) -> None:
        self.pos_err(pos, '%s must be followed by %s', left, right)

    def follow_err_exp(self, pos: Pos, left: ta.Any) -> None:
        self.follow_err(pos, left, 'an expression')

    def follow(self, lpos: Pos, left: str, tok: Token) -> None:
        if not self.got(tok):
            self.follow_err(lpos, left, tok)

    def follow_rsrv(self, lpos: Pos, left: str, val: str) -> Pos:
        pos, ok = self.got_rsrv(val)
        if not ok:
            if self.recover_error():
                return _RECOVERED_POS
            self.follow_err(lpos, left, val)
        return pos

    def follow_stmts(self, left: str, lpos: Pos, *stops: str) -> tuple[list[Stmt], list[Comment]]:
        if self.got(Token.SEMICOLON):
            if lang_in(self.lang, LANG_ZSH | LANG_MIR_BSD_KORN):
                return [], []  # allow an empty list
            self.follow_err(lpos, left, 'a statement list')
            return [], []
        stmts, last = self.stmt_list(*stops)
        if len(stmts) < 1:
            if lang_in(self.lang, LANG_ZSH | LANG_MIR_BSD_KORN):
                return [], []  # allow an empty list
            if self.recover_error():
                return [Stmt(position=_RECOVERED_POS)], []
            self.follow_err(lpos, left, 'a statement list')
        return stmts, last

    def follow_word_tok(self, tok: Token, pos: Pos) -> Word | None:
        w = self.get_word()
        if w is None:
            if self.recover_error():
                return self.word_one(Lit(value_pos=_RECOVERED_POS, value=''))
            self.follow_err(pos, tok, 'a word')
        return w

    def stmt_end(self, n: Node, start: str, end: str) -> Pos:
        pos, ok = self.got_rsrv(end)
        if not ok:
            if self.recover_error():
                return _RECOVERED_POS
            self.pos_err(n.pos(), '%s statement must end with %s', start, end)
        return pos

    def quote_err(self, lpos: Pos, quote: Token) -> None:
        self.pos_err(lpos, 'reached %s without closing quote %s', self.tok, quote)

    def matching_err(self, lpos: Pos, left: Token, right: Token) -> None:
        self.pos_err(lpos, 'reached %s without matching %s with %s', self.tok, left, right)

    def matched(self, lpos: Pos, left: Token, right: Token) -> Pos:
        pos = self.pos
        if not self.got(right):
            if self.recover_error():
                return _RECOVERED_POS
            self.matching_err(lpos, left, right)
        return pos

    def err_pass(self, err: Exception) -> None:
        if self.err is None:
            self.err = err
            self.bsp = len(self.src) + 1
            self.r = _EOF_RUNE
            self.w = 1
            self.tok = Token.EOF_

    def incomplete(self) -> bool:
        return self.open_nodes > 0 or self.lit_bs is not None

    def pos_err(self, pos: Pos, format: str, *args: ta.Any) -> None:
        text = format % args if args else format
        self.err_pass(RuntimeError(text))

    def cur_err(self, format: str, *args: ta.Any) -> None:
        self.pos_err(self.pos, format, *args)

    def check_lang(self, pos: Pos, lang_set: LangVariant, format: str, *a: ta.Any) -> None:
        if lang_in(self.lang, lang_set):
            return
        feature = format % a if a else format
        self.err_pass(RuntimeError(f'{feature} is a {"/".join(str(l) for l in lang_bits(lang_set))} feature'))

    # -- Statement parsing --

    def stmts(self, *stops: str) -> list[Stmt]:
        result: list[Stmt] = []
        got_end = True
        while self.tok != Token.EOF_:
            new_line = self.got(Token.NEWL_)
            if self.tok == Token.LIT_WORD_:
                should_break = False
                for stop in stops:
                    if self.val == stop:
                        should_break = True
                        break
                if should_break:
                    break
                if self.val == '}':
                    self.cur_err('%s can only be used to close a block', Token.RIGHT_BRACE)
            elif self.tok == Token.RIGHT_PAREN:
                if self.quote == _SUB_CMD:
                    break
            elif self.tok == Token.BCK_QUOTE:
                if self.backquote_end():
                    break
            elif self.tok in (Token.DBL_SEMICOLON, Token.SEMI_AND, Token.DBL_SEMI_AND, Token.SEMI_OR):
                if self.quote == _SWITCH_CASE:
                    break
                self.cur_err('%s can only be used in a case clause', self.tok)
            if not new_line and not got_end:
                self.cur_err('statements must be separated by &, ; or a newline')
            if self.tok == Token.EOF_:
                break
            self.open_nodes += 1
            s = self.get_stmt(True, False, False)
            self.open_nodes -= 1
            if s is None:
                self.invalid_stmt_start()
                break
            got_end = s.semicolon.is_valid() if hasattr(s.semicolon, 'is_valid') else bool(s.semicolon)
            result.append(s)
        return result

    def stmt_list(self, *stops: str) -> tuple[list[Stmt], list[Comment]]:
        stmts = self.stmts(*stops)
        split = len(self.acc_coms)
        if self.tok == Token.LIT_WORD_ and self.val in ('elif', 'else', 'fi'):
            for i in range(len(self.acc_coms) - 1, -1, -1):
                c = self.acc_coms[i]
                if c.pos().col() != self.pos.col():
                    break
                split = i
        last: list[Comment] = []
        if split > 0:
            last = self.acc_coms[:split]
        self.acc_coms = self.acc_coms[split:]
        return stmts, last

    def invalid_stmt_start(self) -> None:
        if self.tok in (Token.SEMICOLON, Token.AND, Token.OR, Token.AND_AND, Token.OR_OR):
            self.cur_err('%s can only immediately follow a statement', self.tok)
        elif self.tok == Token.RIGHT_PAREN:
            self.cur_err('%s can only be used to close a subshell', self.tok)
        else:
            self.cur_err('%s is not a valid start for a statement', self.tok)

    def get_word(self) -> Word | None:
        w = self.word_any_number()
        if len(w.parts) > 0 and self.err is None:
            return w
        return None

    def get_lit(self) -> Lit | None:
        if self.tok in (Token.LIT_, Token.LIT_WORD_, Token.LIT_REDIR_):
            l = self.lit(self.pos, self.val)
            self.next()
            return l
        return None

    def word_parts(self, wps: list[WordPart]) -> list[WordPart]:
        if self.quote == _NO_STATE:
            self.quote = _UNQUOTED_WORD_CONT
            try:
                return self._word_parts_inner(wps)
            finally:
                self.quote = _NO_STATE
        return self._word_parts_inner(wps)

    def _word_parts_inner(self, wps: list[WordPart]) -> list[WordPart]:
        while True:
            self.open_nodes += 1
            n = self.word_part()
            self.open_nodes -= 1
            if n is None:
                if len(wps) == 0:
                    return []
                return wps
            wps.append(n)
            if self.spaced:
                return wps

    def ensure_no_nested(self, pos: Pos) -> None:
        if self.forbid_nested:
            self.pos_err(pos, 'expansions not allowed in heredoc words')

    def word_part(self) -> WordPart | None:  # noqa: C901
        from .parser_arithm import arithm_end as _arithm_end
        from .parser_arithm import arithm_matching_err as _arithm_matching_err
        from .parser_arithm import follow_arithm as _follow_arithm

        if self.tok in (Token.LIT_, Token.LIT_WORD_, Token.LIT_REDIR_):
            l = self.lit(self.pos, self.val)
            self.next()
            return l
        elif self.tok == Token.DOLL_BRACE:
            self.ensure_no_nested(self.pos)
            if self.r in ('|', ' ', '\t', '\n'):
                if self.r == '|':
                    self.check_lang(self.pos, LANG_BASH_LIKE | LANG_MIR_BSD_KORN, '`${|stmts;}`')
                else:
                    self.check_lang(self.pos, LANG_BASH_LIKE | LANG_MIR_BSD_KORN, '`${ stmts;}`')
                cs = CmdSubst(
                    left=self.pos,
                    temp_file=self.r != '|',
                    reply_var=self.r == '|',
                )
                old = self.pre_nested(_SUB_CMD)
                self.rune()  # don't tokenize '|'
                self.next()
                cs.stmts, cs.last = self.stmt_list('}')
                self.post_nested(old)
                pos, ok = self.got_rsrv('}')
                if not ok:
                    self.matching_err(cs.left, Token.DOLL_BRACE, Token.RIGHT_BRACE)
                cs.right = pos
                return cs
            else:
                return self.param_exp()
        elif self.tok in (Token.DOLL_DBL_PAREN, Token.DOLL_BRACK):
            self.ensure_no_nested(self.pos)
            left = self.tok
            ar = ArithmExp(left=self.pos, bracket=left == Token.DOLL_BRACK)
            old = self.pre_nested(_ARITHM_EXPR)
            self.next()
            if self.got(Token.HASH):
                self.check_lang(ar.pos(), LANG_MIR_BSD_KORN, 'unsigned expressions')
                ar.unsigned = True
            ar.x = _follow_arithm(self, left, ar.left)
            if ar.bracket:
                if self.tok != Token.RIGHT_BRACK:
                    _arithm_matching_err(self, ar.left, Token.DOLL_BRACK, Token.RIGHT_BRACK)
                self.post_nested(old)
                ar.right = self.pos
                self.next()
            else:
                ar.right = _arithm_end(self, Token.DOLL_DBL_PAREN, ar.left, old)
            return ar
        elif self.tok == Token.DOLL_PAREN:
            self.ensure_no_nested(self.pos)
            return self.cmd_subst()
        elif self.tok == Token.DOLLAR:
            pe = self.param_exp()
            if pe is None:  # was not actually a parameter expansion, like: "foo$"
                l = self.lit(self.pos, '$')
                self.next()
                return l
            self.ensure_no_nested(pe.dollar)
            return pe
        elif (
            (cond_assgn := (self.tok == Token.ASSGN_PAREN))
            or (cond_cmd := (self.tok in (Token.CMD_IN, Token.CMD_OUT)))  # noqa: F841
        ):
            if cond_assgn:
                self.check_lang(self.pos, LANG_ZSH, '%s process substitutions', self.tok)
                # fallthrough
            self.ensure_no_nested(self.pos)
            ps = ProcSubst(op=ProcOperator(self.tok), op_pos=self.pos)
            old = self.pre_nested(_SUB_CMD)
            self.next()
            ps.stmts, ps.last = self.stmt_list()
            self.post_nested(old)
            ps.rparen = self.matched(ps.op_pos, Token(ps.op.value), Token.RIGHT_PAREN)
            return ps
        elif self.tok in (Token.SGL_QUOTE, Token.DOLL_SGL_QUOTE):
            sq = SglQuoted(left=self.pos, dollar=self.tok == Token.DOLL_SGL_QUOTE)
            r = self.r
            from .lexer import end_lit
            from .lexer import new_lit
            new_lit(self, r)
            while True:
                if r == '\\':
                    if sq.dollar:
                        self.rune()
                elif r == '\'':
                    sq.right = self.next_pos()
                    sq.value = end_lit(self)
                    self.rune()
                    self.next()
                    return sq
                elif r == _ESC_NEWL:
                    self.lit_bs.append('\\')
                    self.lit_bs.append('\n')
                elif r == _EOF_RUNE:
                    self.tok = Token.EOF_
                    if self.recover_error():
                        sq.right = _RECOVERED_POS
                        return sq
                    self.quote_err(sq.pos(), Token.SGL_QUOTE)
                    return None
                r = self.rune()
        elif self.tok in (Token.DBL_QUOTE, Token.DOLL_DBL_QUOTE):
            if self.quote == _DBL_QUOTES:
                return None
            return self.dbl_quoted()
        elif self.tok == Token.BCK_QUOTE:
            if self.backquote_end():
                return None
            self.ensure_no_nested(self.pos)
            cs = CmdSubst(left=self.pos, backquotes=True)
            old = self.pre_nested(_SUB_CMD_BCKQUO)
            self.open_bquotes += 1

            # The lexer didn't call p.rune for us, so that it could have
            # the right p.openBquotes to properly handle backslashes.
            self.rune()

            self.next()
            cs.stmts, cs.last = self.stmt_list()
            if self.tok == Token.BCK_QUOTE and self.last_bquote_esc < self.open_bquotes - 1:
                self.tok = Token.EOF_
                self.quote_err(cs.pos(), Token.BCK_QUOTE)
            self.post_nested(old)
            self.open_bquotes -= 1
            cs.right = self.pos

            # Like above, the lexer didn't call p.rune for us.
            self.rune()
            if not self.got(Token.BCK_QUOTE):
                if self.recover_error():
                    cs.right = _RECOVERED_POS
                else:
                    self.quote_err(cs.pos(), Token.BCK_QUOTE)
            return cs
        elif self.tok in (Token.GLOB_QUEST, Token.GLOB_STAR, Token.GLOB_PLUS, Token.GLOB_AT, Token.GLOB_EXCL):
            self.check_lang(self.pos, LANG_BASH_LIKE | LANG_MIR_BSD_KORN, 'extended globs')
            eg = ExtGlob(op=GlobOperator(self.tok), op_pos=self.pos)
            lparens = 1
            r = self.r
            from .lexer import end_lit
            from .lexer import new_lit
            new_lit(self, r)
            while True:
                if r == _EOF_RUNE:
                    break
                elif r == '(':
                    lparens += 1
                elif r == ')':
                    lparens -= 1
                    if lparens == 0:
                        break
                r = self.rune()
            eg.pattern = self.lit(pos_add_col(eg.op_pos, 2), end_lit(self))
            self.rune()
            self.next()
            if lparens != 0:
                self.matching_err(eg.op_pos, Token(eg.op.value), Token.RIGHT_PAREN)
            return eg
        else:
            return None

    def cmd_subst(self) -> CmdSubst:
        cs = CmdSubst(left=self.pos)
        old = self.pre_nested(_SUB_CMD)
        self.next()
        cs.stmts, cs.last = self.stmt_list()
        self.post_nested(old)
        cs.right = self.matched(cs.left, Token.DOLL_PAREN, Token.RIGHT_PAREN)
        return cs

    def dbl_quoted(self) -> DblQuoted:
        q = DblQuoted(left=self.pos, dollar=self.tok == Token.DOLL_DBL_QUOTE)
        old = self.quote
        self.quote = _DBL_QUOTES
        self.next()
        q.parts = self.word_parts([])
        self.quote = old
        q.right = self.pos
        if not self.got(Token.DBL_QUOTE):
            if self.recover_error():
                q.right = _RECOVERED_POS
            else:
                self.quote_err(q.pos(), Token.DBL_QUOTE)
        return q

    def param_exp(self) -> ParamExp | None:  # noqa: C901
        from .lexer import end_lit
        from .lexer import new_lit
        from .lexer import param_token

        old = self.quote
        self.quote = _RUNE_BY_RUNE
        pe = ParamExp(
            dollar=self.pos,
            short=self.tok == Token.DOLLAR,
        )
        if not pe.short and self.r == '(':
            self.check_lang(pe.pos(), LANG_ZSH, 'parameter expansion flags')
            lparen = self.next_pos()
            self.rune()
            self.pos = self.next_pos()
            new_lit(self, self.r)
            while self.r != _EOF_RUNE:
                if self.r == ')':
                    break
                self.rune()
            self.val = end_lit(self)
            if self.r != ')':
                self.tok = Token.EOF_
                self.matching_err(lparen, Token.LEFT_PAREN, Token.RIGHT_PAREN)
            pe.flags = self.lit(self.pos, self.val)
            self.rune()
        if not pe.short or lang_in(self.lang, LANG_ZSH):
            if self.r == '#':
                r2 = self.peek()
                if r2 == _EOF_RUNE or single_rune_param(r2) or param_name_rune(r2) or r2 == '"':
                    pe.length = True
                    self.rune()
            elif self.r == '%':
                r2 = self.peek()
                if r2 == _EOF_RUNE or single_rune_param(r2) or param_name_rune(r2) or r2 == '"':
                    self.check_lang(pe.pos(), LANG_MIR_BSD_KORN, '`${%%foo}`')
                    pe.width = True
                    self.rune()
            elif self.r == '!':
                r2 = self.peek()
                if r2 == _EOF_RUNE or single_rune_param(r2) or param_name_rune(r2) or r2 == '"':
                    self.check_lang(pe.pos(), LANG_BASH_LIKE | LANG_MIR_BSD_KORN, '`${!foo}`')
                    pe.excl = True
                    self.rune()
            elif self.r == '+':
                r2 = self.peek()
                if r2 == _EOF_RUNE or single_rune_param(r2) or param_name_rune(r2) or r2 == '"':
                    self.check_lang(pe.pos(), LANG_ZSH, '`${+foo}`')
                    pe.plus = True
                    self.rune()
        pe = self._param_exp_parameter(pe)
        if pe is None:
            self.quote = old
            return None  # just "$"
        if pe.short:
            if lang_in(self.lang, LANG_ZSH) and self.r == '[':
                self.pos = self.next_pos()
                self.rune()
                pe.index = self.either_index()
            self.quote = old
            self.next()
            return pe
        # Index expressions
        if self.r == '[':
            self.check_lang(self.next_pos(), LANG_BASH_LIKE | LANG_MIR_BSD_KORN | LANG_ZSH, 'arrays')
            if pe.param is not None and not valid_name(pe.param.value):
                self.pos_err(self.next_pos(), 'cannot index a special parameter name')
            self.pos = self.next_pos()
            self.rune()
            pe.index = self.either_index()
        tok_rune = self.r
        self.pos = self.next_pos()
        self.tok = param_token(self, self.r)
        if self.tok == Token.RIGHT_BRACE:
            pe.rbrace = self.pos
            self.quote = old
            self.next()
            return pe
        if self.tok != Token.EOF_ and (pe.length or pe.width or pe.plus):
            self.cur_err('cannot combine multiple parameter expansion operators')
        if self.tok in (Token.SLASH, Token.DBL_SLASH):  # pattern search and replace
            self.check_lang(self.pos, LANG_BASH_LIKE | LANG_MIR_BSD_KORN | LANG_ZSH, 'search and replace')
            pe.repl = Replace(all=self.tok == Token.DBL_SLASH)
            self.quote = _PARAM_EXP_REPL
            self.next()
            pe.repl.orig = self.get_word()
            self.quote = _PARAM_EXP_EXP
            if self.got(Token.SLASH):
                pe.repl.with_ = self.get_word()
        elif self.tok == Token.COLON:  # slicing
            if lang_in(self.lang, LANG_ZSH) and (self.r == '&' or ascii_letter(self.r)):
                pos2 = self.pos
                new_lit(self, self.r)
                while True:
                    if self.r == _EOF_RUNE:
                        self.tok = Token.EOF_
                        self.matching_err(pe.dollar, Token.DOLL_BRACE, Token.RIGHT_BRACE)
                        break
                    elif self.r == '}':
                        if pe.modifiers is None:
                            pe.modifiers = []
                        pe.modifiers.append(self.lit(pos2, end_lit(self)))
                        pe.rbrace = self.next_pos()
                        self.rune()
                        break
                    elif self.r == ':':
                        if pe.modifiers is None:
                            pe.modifiers = []
                        pe.modifiers.append(self.lit(pos2, end_lit(self)))
                        self.rune()
                        pos2 = self.next_pos()
                        new_lit(self, self.r)
                    else:
                        self.rune()
                self.quote = old
                self.next()
                return pe
            self.check_lang(self.pos, LANG_BASH_LIKE | LANG_MIR_BSD_KORN | LANG_ZSH, 'slicing')
            pe.slice = Slice()
            colon_pos = self.pos
            self.quote = _PARAM_EXP_ARITHM
            self.next()
            if self.tok != Token.COLON:
                from .parser_arithm import follow_arithm as _follow_arithm
                pe.slice.offset = _follow_arithm(self, Token.COLON, colon_pos)
            colon_pos = self.pos
            if self.got(Token.COLON):
                from .parser_arithm import follow_arithm as _follow_arithm
                pe.slice.length = _follow_arithm(self, Token.COLON, colon_pos)
            self.quote = old
            pe.rbrace = self.pos
            from .parser_arithm import matched_arithm as _matched_arithm
            _matched_arithm(self, pe.dollar, Token.DOLL_BRACE, Token.RIGHT_BRACE)
            return pe
        elif self.tok in (Token.CARET, Token.DBL_CARET, Token.COMMA, Token.DBL_COMMA):
            self.check_lang(self.pos, LANG_BASH_LIKE, 'this expansion operator')
            pe.exp = self._param_exp_exp()
        elif self.tok in (Token.AT, Token.STAR):
            if self.tok == Token.STAR and not pe.excl:
                self.cur_err('not a valid parameter expansion operator: %s', self.tok)
            elif pe.excl and self.r == '}':
                self.check_lang(pe.pos(), LANG_BASH_LIKE, '`${!foo%s}`', self.tok)
                pe.names = ParNamesOperator(self.tok)
                self.next()
            elif self.tok == Token.AT:
                self.check_lang(self.pos, LANG_BASH_LIKE | LANG_MIR_BSD_KORN, 'this expansion operator')
                pe.exp = self._param_exp_exp()
            else:
                pe.exp = self._param_exp_exp()
        elif self.tok in (
            Token.PLUS, Token.COL_PLUS, Token.MINUS, Token.COL_MINUS,
            Token.QUEST, Token.COL_QUEST, Token.ASSGN, Token.COL_ASSGN,
            Token.PERC, Token.DBL_PERC, Token.HASH, Token.DBL_HASH, Token.COL_HASH,
        ):
            pe.exp = self._param_exp_exp()
        elif self.tok == Token.EOF_:
            pass
        else:
            if param_name_rune(tok_rune):
                if pe.param is not None:
                    self.cur_err('%s cannot be followed by a word', pe.param.value)
                else:
                    self.cur_err('nested parameter expansion cannot be followed by a word')
            else:
                self.cur_err('not a valid parameter expansion operator: %s', tok_rune)
        if self.tok != Token.EOF_ and self.tok != Token.RIGHT_BRACE:
            self.tok = param_token(self, self.r)
        self.quote = old
        pe.rbrace = self.matched(pe.dollar, Token.DOLL_BRACE, Token.RIGHT_BRACE)
        return pe

    def _param_exp_parameter(self, pe: ParamExp) -> ParamExp | None:
        from .lexer import end_lit
        from .lexer import new_lit

        # Check for Zsh nested parameter expressions
        # TODO: nestedParameterStart translation - simplified for now
        if self.r in ('?', '-'):
            if pe.length and self.peek() != '}':
                pe.length = False
                pos = self.next_pos()
                pe.param = self.lit(pos_add_col(pos, -1), '#')
                pe.param.value_end = pos
            else:
                r2, pos = self.r, self.next_pos()
                self.rune()
                pe.param = self.lit(pos, r2)
        elif self.r in ('@', '*', '#', '!', '$'):
            r2, pos = self.r, self.next_pos()
            self.rune()
            pe.param = self.lit(pos, r2)
        else:
            pos = self.next_pos()
            if pe.short and single_rune_param(self.r):
                self.val = self.r
                self.rune()
            else:
                new_lit(self, self.r)
                while self.r != _EOF_RUNE:
                    if not param_name_rune(self.r) and self.r != _ESC_NEWL:
                        break
                    self.rune()
                self.val = end_lit(self)
                if not number_literal(self.val) and not valid_name(self.val):
                    if pe.short:
                        return None  # just "$"
                    self.pos_err(pos, 'invalid parameter name')
            pe.param = self.lit(pos, self.val)
        return pe

    def _param_exp_exp(self) -> Expansion:
        op = ParExpOperator(self.tok)
        self.quote = _PARAM_EXP_EXP
        self.next()
        if op == ParExpOperator.OTHER_PARAMOPS:
            if self.tok not in (Token.LIT_, Token.LIT_WORD_):
                self.cur_err('@ expansion operator requires a literal')
            if self.val in ('a', 'k', 'u', 'A', 'E', 'K', 'L', 'P', 'U'):
                self.check_lang(self.pos, LANG_BASH_LIKE, 'this expansion operator')
            elif self.val == '#':
                self.check_lang(self.pos, LANG_MIR_BSD_KORN, 'this expansion operator')
            elif self.val == 'Q':
                pass
            else:
                self.cur_err('invalid @ expansion operator %s', self.val)
        return Expansion(op=op, word=self.get_word())

    def either_index(self) -> ta.Any:
        from .parser_arithm import follow_arithm as _follow_arithm
        from .parser_arithm import matched_arithm as _matched_arithm

        old = self.quote
        lpos = self.pos
        self.quote = _PARAM_EXP_ARITHM
        self.next()
        if self.tok == Token.STAR or self.tok == Token.AT:
            self.tok, self.val = Token.LIT_WORD_, str(self.tok)
        expr = _follow_arithm(self, Token.LEFT_BRACK, lpos)
        self.quote = old
        _matched_arithm(self, lpos, Token.LEFT_BRACK, Token.RIGHT_BRACK)
        return expr

    def zsh_sub_flags(self) -> FlagsArithm:
        from .lexer import end_lit
        from .lexer import new_lit
        from .parser_arithm import arithm_expr_assign

        zf = FlagsArithm()
        lparen = self.pos
        old = self.quote
        self.quote = _RUNE_BY_RUNE
        self.pos = self.next_pos()
        new_lit(self, self.r)
        while self.r != _EOF_RUNE:
            if self.r == ')':
                break
            self.rune()
        self.val = end_lit(self)
        if self.r != ')':
            self.tok = Token.EOF_
            self.matching_err(lparen, Token.LEFT_PAREN, Token.RIGHT_PAREN)
        zf.flags = self.lit(self.pos, self.val)
        self.rune()
        self.quote = old
        self.next()
        if self.tok == Token.STAR or self.tok == Token.AT:
            self.tok, self.val = Token.LIT_WORD_, str(self.tok)
        zf.x = arithm_expr_assign(self, False)
        return zf

    def stop_token(self) -> bool:
        if self.tok in (
            Token.EOF_, Token.NEWL_, Token.SEMICOLON, Token.AND, Token.OR,
            Token.AND_AND, Token.OR_OR, Token.OR_AND,
            Token.DBL_SEMICOLON, Token.SEMI_AND, Token.DBL_SEMI_AND, Token.SEMI_OR,
            Token.RIGHT_PAREN,
        ):
            return True
        if self.tok == Token.BCK_QUOTE:
            return self.backquote_end()
        return False

    def backquote_end(self) -> bool:
        return self.last_bquote_esc < self.open_bquotes

    def has_valid_ident(self) -> bool:
        if self.tok != Token.LIT_ and self.tok != Token.LIT_WORD_:
            return False
        end = self.eql_offs
        if end > 0:
            if self.val[end - 1] == '+' and lang_in(self.lang, LANG_BASH_LIKE | LANG_MIR_BSD_KORN | LANG_ZSH):
                end -= 1  # a+=x
            if valid_name(self.val[:end]):
                return True
        elif not valid_name(self.val):
            return False  # *[i]=x
        return self.r == '['  # a[i]=x

    def get_assign(self, need_equal: bool) -> Assign:
        as_ = Assign()
        if self.eql_offs > 0:  # foo=bar
            name_end = self.eql_offs
            if (
                lang_in(self.lang, LANG_BASH_LIKE | LANG_MIR_BSD_KORN | LANG_ZSH)
                and self.val[self.eql_offs - 1] == '+'
            ):
                as_.append = True
                name_end -= 1
            as_.name = self.lit(self.pos, self.val[:name_end])
            as_.name.value_end = pos_add_col(as_.name.value_pos, name_end)
            left = self.lit(pos_add_col(self.pos, 1), self.val[self.eql_offs + 1:])
            if left.value != '':
                left.value_pos = pos_add_col(left.value_pos, self.eql_offs)
                as_.value = self.word_one(left)
            self.next()
        else:  # foo[x]=bar
            as_.name = self.lit(self.pos, self.val)
            self.rune()
            self.pos = pos_add_col(self.pos, 1)
            as_.index = self.either_index()
            if self.spaced or self.stop_token():
                if need_equal:
                    self.follow_err(as_.pos(), 'a[b]', Token.ASSGN)
                else:
                    as_.naked = True
                    return as_
            if self.tok == Token.ASSGN_PAREN:
                self.cur_err('arrays cannot be nested')
                return as_
            if len(self.val) > 0 and self.val[0] == '+':
                as_.append = True
                self.val = self.val[1:]
                self.pos = pos_add_col(self.pos, 1)
            if len(self.val) < 1 or self.val[0] != '=':
                if as_.append:
                    self.follow_err(as_.pos(), 'a[b]+', Token.ASSGN)
                else:
                    self.follow_err(as_.pos(), 'a[b]', Token.ASSGN)
                return as_
            self.pos = pos_add_col(self.pos, 1)
            self.val = self.val[1:]
            if self.val == '':
                self.next()
        if self.spaced or self.stop_token():
            return as_
        if as_.value is None and self.tok == Token.LEFT_PAREN:
            self.check_lang(self.pos, LANG_BASH_LIKE | LANG_MIR_BSD_KORN | LANG_ZSH, 'arrays')
            as_.array = ArrayExpr(lparen=self.pos)
            new_quote = self.quote
            if lang_in(self.lang, LANG_BASH_LIKE | LANG_ZSH):
                new_quote = _ARRAY_ELEMS
            old = self.pre_nested(new_quote)
            self.next()
            self.got(Token.NEWL_)
            while self.tok != Token.EOF_ and self.tok != Token.RIGHT_PAREN:
                ae = ArrayElem()
                ae.comments, self.acc_coms = self.acc_coms, []
                if self.tok == Token.LEFT_BRACK:
                    left2 = self.pos
                    ae.index = self.either_index()
                    if self.tok == Token.ASSGN_PAREN:
                        self.cur_err('arrays cannot be nested')
                        return as_
                    self.follow(left2, '[x]', Token.ASSGN)
                ae.value = self.get_word()
                if ae.value is None:
                    if self.tok not in (Token.NEWL_, Token.RIGHT_PAREN, Token.LEFT_BRACK):
                        self.cur_err('array element values must be words')
                        return as_
                if len(self.acc_coms) > 0:
                    c = self.acc_coms[0]
                    if c.pos().line() == ae.end().line():
                        ae.comments.append(c)
                        self.acc_coms = self.acc_coms[1:]
                as_.array.elems.append(ae)
                self.got(Token.NEWL_)
            as_.array.last, self.acc_coms = self.acc_coms, []
            self.post_nested(old)
            as_.array.rparen = self.matched(as_.array.lparen, Token.LEFT_PAREN, Token.RIGHT_PAREN)
        else:
            w = self.get_word()
            if w is not None:
                if as_.value is None:
                    as_.value = w
                else:
                    as_.value.parts.extend(w.parts)
        return as_

    def peek_redir(self) -> bool:
        return self.tok in (
            Token.LIT_REDIR_,
            Token.RDR_OUT, Token.APP_OUT, Token.RDR_IN, Token.RDR_IN_OUT,
            Token.DPL_IN, Token.DPL_OUT, Token.RDR_CLOB, Token.RDR_TRUNC,
            Token.APP_CLOB, Token.APP_TRUNC,
            Token.HDOC, Token.DASH_HDOC, Token.WORD_HDOC,
            Token.RDR_ALL, Token.RDR_ALL_CLOB, Token.RDR_ALL_TRUNC,
            Token.APP_ALL, Token.APP_ALL_CLOB, Token.APP_ALL_TRUNC,
        )

    def do_redirect(self, s: Stmt) -> None:
        r = Redirect()
        if s.redirs is None:
            s.redirs = []
        s.redirs.append(r)
        r.n = self.get_lit()
        if r.n is not None and r.n.value[0] == '{':
            self.check_lang(r.n.pos(), LANG_BASH_LIKE, '`{varname}` redirects')
        r.op, r.op_pos = RedirOperator(self.tok), self.pos
        if r.op in (RedirOperator.RDR_ALL, RedirOperator.APP_ALL):
            self.check_lang(self.pos, LANG_BASH_LIKE | LANG_MIR_BSD_KORN | LANG_ZSH, '%s redirects', r.op)
        elif r.op in (
            RedirOperator.RDR_TRUNC, RedirOperator.APP_CLOB, RedirOperator.APP_TRUNC,
            RedirOperator.RDR_ALL_CLOB, RedirOperator.RDR_ALL_TRUNC,
            RedirOperator.APP_ALL_CLOB, RedirOperator.APP_ALL_TRUNC,
        ):
            self.check_lang(self.pos, LANG_ZSH, '%s redirects', r.op)
        self.next()
        if r.op in (RedirOperator.HDOC, RedirOperator.DASH_HDOC):
            old = self.quote
            self.quote, self.forbid_nested = _HDOC_WORD, True
            self.heredocs.append(r)
            r.word = self.follow_word_tok(Token(r.op.value), r.op_pos)
            self.quote, self.forbid_nested = old, False
            if self.tok == Token.NEWL_:
                if len(self.acc_coms) > 0:
                    c = self.acc_coms[0]
                    if c.pos().line() == s.end().line():
                        s.comments.append(c)
                        self.acc_coms = self.acc_coms[1:]
                self.do_heredocs()
        elif (
            (cond_wh := (r.op == RedirOperator.WORD_HDOC))
            or (cond_default := True)  # noqa: F841
        ):
            if cond_wh:
                self.check_lang(r.op_pos, LANG_BASH_LIKE | LANG_MIR_BSD_KORN | LANG_ZSH, 'herestrings')
                # fallthrough to default
            r.word = self.follow_word_tok(Token(r.op.value), r.op_pos)

    def get_stmt(self, read_end: bool, bin_cmd: bool, fn_body: bool) -> Stmt | None:
        pos, ok = self.got_rsrv('!')
        s = Stmt(position=pos)
        if ok:
            s.negated = True
            if self.stop_token():
                self.pos_err(s.pos(), '%s cannot form a statement alone', Token.EXCL_MARK)
            _, ok2 = self.got_rsrv('!')
            if ok2:
                self.pos_err(s.pos(), 'cannot negate a command multiple times')
        s = self.got_stmt_pipe(s, False)
        if s is None or self.err is not None:
            return None
        # instead of using recursion, iterate manually
        while self.tok == Token.AND_AND or self.tok == Token.OR_OR:
            if bin_cmd:
                return s
            b = BinaryCmd(
                op_pos=self.pos,
                op=BinCmdOperator(self.tok),
                x=s,
            )
            self.next()
            self.got(Token.NEWL_)
            b.y = self.get_stmt(False, True, False)
            if b.y is None or self.err is not None:
                if self.recover_error():
                    b.y = Stmt(position=_RECOVERED_POS)
                else:
                    self.follow_err(b.op_pos, b.op, 'a statement')
                    return None
            s = Stmt(position=s.position)
            s.cmd = b
            s.comments, b.x.comments = b.x.comments, []
        if read_end:
            if self.tok == Token.SEMICOLON:
                s.semicolon = self.pos
                self.next()
            elif self.tok == Token.AND:
                s.semicolon = self.pos
                self.next()
                s.background = True
            elif self.tok == Token.OR_AND:
                s.semicolon = self.pos
                self.next()
                s.coprocess = True
        if len(self.acc_coms) > 0 and not bin_cmd and not fn_body:
            c = self.acc_coms[0]
            if c.pos().line() == s.end().line():
                s.comments.append(c)
                self.acc_coms = self.acc_coms[1:]
        return s

    def got_stmt_pipe(self, s: Stmt, bin_cmd: bool) -> Stmt | None:  # noqa: C901
        s.comments, self.acc_coms = self.acc_coms, []
        while self.peek_redir():
            self.do_redirect(s)
        redirs_start = len(s.redirs) if s.redirs else 0
        if self.tok == Token.LIT_WORD_:
            if self.val == '{':
                self.block(s)
            elif self.val == '{}':
                if lang_in(self.lang, LANG_ZSH):
                    s.cmd = Block(lbrace=self.pos, rbrace=pos_add_col(self.pos, 1))
                    self.next()
            elif self.val == 'if':
                self.if_clause(s)
            elif self.val in ('while', 'until'):
                self.while_clause(s, self.val == 'until')
            elif self.val == 'for':
                self.for_clause(s)
            elif self.val == 'case':
                self.case_clause(s)
            elif self.val == '}':
                self.cur_err('%s can only be used to close a block', Token.RIGHT_BRACE)
            elif self.val in ('then', 'elif'):
                self.cur_err('%s can only be used in an `if`', self.val)
            elif self.val == 'fi':
                self.cur_err('%s can only be used to end an `if`', self.val)
            elif self.val == 'do':
                self.cur_err('%s can only be used in a loop', self.val)
            elif self.val == 'done':
                self.cur_err('%s can only be used to end a loop', self.val)
            elif self.val == 'esac':
                self.cur_err('%s can only be used to end a `case`', self.val)
            elif self.val == '!':
                if not s.negated:
                    self.cur_err('%s can only be used in full statements', Token.EXCL_MARK)
            elif self.val == '[[':
                if lang_in(self.lang, LANG_BASH_LIKE | LANG_MIR_BSD_KORN | LANG_ZSH):
                    self.test_clause(s)
            elif self.val == ']]':
                if lang_in(self.lang, LANG_BASH_LIKE | LANG_MIR_BSD_KORN | LANG_ZSH):
                    self.cur_err('%s can only be used to close a test', Token.DBL_RIGHT_BRACK)
            elif self.val == 'let':
                if lang_in(self.lang, LANG_BASH_LIKE | LANG_MIR_BSD_KORN | LANG_ZSH):
                    self.let_clause(s)
            elif self.val == 'function':
                if lang_in(self.lang, LANG_BASH_LIKE | LANG_MIR_BSD_KORN | LANG_ZSH):
                    self.bash_func_decl(s)
            elif self.val == 'declare':
                if lang_in(self.lang, LANG_BASH_LIKE | LANG_ZSH):
                    self.decl_clause(s)
            elif self.val in ('local', 'export', 'readonly', 'typeset', 'nameref'):
                if lang_in(self.lang, LANG_BASH_LIKE | LANG_MIR_BSD_KORN | LANG_ZSH):
                    self.decl_clause(s)
            elif self.val == 'time':
                if lang_in(self.lang, LANG_BASH_LIKE | LANG_MIR_BSD_KORN | LANG_ZSH):
                    self.time_clause(s)
            elif self.val == 'coproc':
                if lang_in(self.lang, LANG_BASH_LIKE):
                    self.coproc_clause(s)
            elif self.val == 'select':
                if lang_in(self.lang, LANG_BASH_LIKE | LANG_MIR_BSD_KORN | LANG_ZSH):
                    self.select_clause(s)
            elif self.val == '@test':
                if lang_in(self.lang, LANG_BATS):
                    self.test_decl(s)
            if s.cmd is not None:
                pass  # already handled
            elif self.has_valid_ident():
                self.call_expr(s, None, True)
            else:
                name = self.lit(self.pos, self.val)
                self.next()
                if self.got(Token.LEFT_PAREN):
                    self.follow(name.value_pos, 'foo(', Token.RIGHT_PAREN)
                    if lang_in(self.lang, LANG_POSIX) and not valid_name(name.value):
                        self.pos_err(name.pos(), 'invalid func name')
                    self.func_decl(s, name.value_pos, False, True, [name])
                else:
                    self.call_expr(s, self.word_one(name), False)
        elif (
            (cond_bck2 := (self.tok == Token.BCK_QUOTE))
            or (cond_lit2 := (self.tok in (  # noqa: F841
                Token.LIT_,
                Token.DOLL_BRACE, Token.DOLL_DBL_PAREN, Token.DOLL_PAREN,
                Token.DOLLAR, Token.CMD_IN, Token.ASSGN_PAREN, Token.CMD_OUT,
                Token.SGL_QUOTE, Token.DOLL_SGL_QUOTE,
                Token.DBL_QUOTE, Token.DOLL_DBL_QUOTE, Token.DOLL_BRACK,
                Token.GLOB_QUEST, Token.GLOB_STAR, Token.GLOB_PLUS,
                Token.GLOB_AT, Token.GLOB_EXCL,
            )))
        ):
            if cond_bck2:
                if self.backquote_end():
                    pass  # break - don't enter the block below
                else:
                    cond_lit2 = True  # fallthrough
            if cond_lit2:  # noqa: F821
                if self.has_valid_ident():
                    self.call_expr(s, None, True)
                else:
                    w = self.word_any_number()
                    if self.got(Token.LEFT_PAREN):
                        self.pos_err(w.pos(), 'invalid func name')
                    self.call_expr(s, w, False)
        elif self.tok == Token.LEFT_PAREN:
            if self.r == ')':
                self.rune()
                fpos = self.pos
                self.next()
                if self.tok == Token.LIT_WORD_ and self.val == '{':
                    self.check_lang(fpos, LANG_ZSH, 'anonymous functions')
                self.func_decl(s, fpos, False, True)
            else:
                self.subshell(s)
        elif self.tok == Token.DBL_LEFT_PAREN:
            self.arithm_exp_cmd(s)
        if s.cmd is None and (s.redirs is None or len(s.redirs) == 0):
            return None  # no statement found
        if redirs_start > 0 and s.cmd is not None:
            if not isinstance(s.cmd, CallExpr):
                self.check_lang(s.pos(), LANG_ZSH, 'redirects before compound commands')
        while self.peek_redir():
            self.do_redirect(s)
        # instead of using recursion, iterate manually
        while self.tok == Token.OR or self.tok == Token.OR_AND:
            if bin_cmd:
                return s
            if self.tok == Token.OR_AND and lang_in(self.lang, LANG_MIR_BSD_KORN):
                break
            b = BinaryCmd(op_pos=self.pos, op=BinCmdOperator(self.tok), x=s)
            self.next()
            self.got(Token.NEWL_)
            b.y = self.got_stmt_pipe(Stmt(position=self.pos), True)
            if b.y is None or self.err is not None:
                if self.recover_error():
                    b.y = Stmt(position=_RECOVERED_POS)
                else:
                    self.follow_err(b.op_pos, b.op, 'a statement')
                    break
            s = Stmt(position=s.position)
            s.cmd = b
            s.comments, b.x.comments = b.x.comments, []
            # in "! x | y", the bang applies to the entire pipeline
            s.negated = b.x.negated
            b.x.negated = False
        return s

    def subshell(self, s: Stmt) -> None:
        sub = Subshell(lparen=self.pos)
        old = self.pre_nested(_SUB_CMD)
        self.next()
        sub.stmts, sub.last = self.follow_stmts('(', sub.lparen)
        self.post_nested(old)
        sub.rparen = self.matched(sub.lparen, Token.LEFT_PAREN, Token.RIGHT_PAREN)
        s.cmd = sub

    def arithm_exp_cmd(self, s: Stmt) -> None:
        from .parser_arithm import arithm_end as _arithm_end
        from .parser_arithm import follow_arithm as _follow_arithm

        ar = ArithmCmd(left=self.pos)
        old = self.pre_nested(_ARITHM_EXPR_CMD)
        self.next()
        if self.got(Token.HASH):
            self.check_lang(ar.pos(), LANG_MIR_BSD_KORN, 'unsigned expressions')
            ar.unsigned = True
        ar.x = _follow_arithm(self, Token.DBL_LEFT_PAREN, ar.left)
        ar.right = _arithm_end(self, Token.DBL_LEFT_PAREN, ar.left, old)
        s.cmd = ar

    def block(self, s: Stmt) -> None:
        b = Block(lbrace=self.pos)
        self.next()
        b.stmts, b.last = self.follow_stmts('{', b.lbrace, '}')
        pos, ok = self.got_rsrv('}')
        if ok:
            b.rbrace = pos
        elif self.recover_error():
            b.rbrace = _RECOVERED_POS
        else:
            self.matching_err(b.lbrace, Token.LEFT_BRACE, Token.RIGHT_BRACE)
        s.cmd = b

    def if_clause(self, s: Stmt) -> None:
        root_if = IfClause(position=self.pos)
        self.next()
        root_if.cond, root_if.cond_last = self.follow_stmts('if', root_if.position, 'then')
        root_if.then_pos = self.follow_rsrv(root_if.position, 'if <cond>', 'then')
        root_if.then, root_if.then_last = self.follow_stmts('then', root_if.then_pos, 'fi', 'elif', 'else')
        cur_if = root_if
        while self.tok == Token.LIT_WORD_ and self.val == 'elif':
            elf = IfClause(position=self.pos)
            cur_if.last = self.acc_coms
            self.acc_coms = []
            self.next()
            elf.cond, elf.cond_last = self.follow_stmts('elif', elf.position, 'then')
            elf.then_pos = self.follow_rsrv(elf.position, 'elif <cond>', 'then')
            elf.then, elf.then_last = self.follow_stmts('then', elf.then_pos, 'fi', 'elif', 'else')
            cur_if.else_ = elf
            cur_if = elf
        else_pos, ok = self.got_rsrv('else')
        if ok:
            cur_if.last = self.acc_coms
            self.acc_coms = []
            els = IfClause(position=else_pos)
            els.then, els.then_last = self.follow_stmts('else', els.position, 'fi')
            cur_if.else_ = els
            cur_if = els
        cur_if.last = self.acc_coms
        self.acc_coms = []
        root_if.fi_pos = self.stmt_end(root_if, 'if', 'fi')
        els2 = root_if.else_
        while els2 is not None:
            els2.fi_pos = root_if.fi_pos
            els2 = els2.else_
        s.cmd = root_if

    def while_clause(self, s: Stmt, until: bool) -> None:
        wc = WhileClause(while_pos=self.pos, until=until)
        rsrv = 'while'
        rsrv_cond = 'while <cond>'
        if wc.until:
            rsrv = 'until'
            rsrv_cond = 'until <cond>'
        self.next()
        wc.cond, wc.cond_last = self.follow_stmts(rsrv, wc.while_pos, 'do')
        wc.do_pos = self.follow_rsrv(wc.while_pos, rsrv_cond, 'do')
        wc.do, wc.do_last = self.follow_stmts('do', wc.do_pos, 'done')
        wc.done_pos = self.stmt_end(wc, rsrv, 'done')
        s.cmd = wc

    def for_clause(self, s: Stmt) -> None:
        fc = ForClause(for_pos=self.pos)
        self.next()
        fc.loop = self.loop(fc.for_pos)

        start, end = 'do', 'done'
        pos, ok = self.got_rsrv('{')
        if ok:
            self.check_lang(pos, LANG_BASH_LIKE | LANG_MIR_BSD_KORN, 'for loops with braces')
            fc.do_pos = pos
            fc.braces = True
            start, end = '{', '}'
        else:
            fc.do_pos = self.follow_rsrv(fc.for_pos, 'for foo [in words]', start)

        s.comments.extend(self.acc_coms)
        self.acc_coms = []
        fc.do, fc.do_last = self.follow_stmts(start, fc.do_pos, end)
        fc.done_pos = self.stmt_end(fc, 'for', end)
        s.cmd = fc

    def loop(self, fpos: Pos) -> ta.Any:
        from .parser_arithm import arithm_end as _arithm_end
        from .parser_arithm import arithm_expr as _arithm_expr

        if self.tok in (Token.LEFT_PAREN, Token.DBL_LEFT_PAREN):
            self.check_lang(self.pos, LANG_BASH_LIKE | LANG_ZSH, 'c-style fors')
        if self.tok == Token.DBL_LEFT_PAREN:
            cl = CStyleLoop(lparen=self.pos)
            old = self.pre_nested(_ARITHM_EXPR_CMD)
            self.next()
            cl.init = _arithm_expr(self, False)
            if not self.got(Token.DBL_SEMICOLON):
                self.follow(self.pos, 'expr', Token.SEMICOLON)
                cl.cond = _arithm_expr(self, False)
                self.follow(self.pos, 'expr', Token.SEMICOLON)
            cl.post = _arithm_expr(self, False)
            cl.rparen = _arithm_end(self, Token.DBL_LEFT_PAREN, cl.lparen, old)
            self.got(Token.SEMICOLON)
            self.got(Token.NEWL_)
            return cl
        return self.word_iter('for', fpos)

    def word_iter(self, ftok: str, fpos: Pos) -> WordIter:
        wi = WordIter()
        wi.name = self.get_lit()
        if wi.name is None:
            self.follow_err(fpos, ftok, 'a literal')
        if self.got(Token.SEMICOLON):
            self.got(Token.NEWL_)
            return wi
        self.got(Token.NEWL_)
        pos, ok = self.got_rsrv('in')
        if ok:
            wi.in_pos = pos
            while not self.stop_token():
                w = self.get_word()
                if w is None:
                    self.cur_err('word list can only contain words')
                else:
                    wi.items.append(w)
            self.got(Token.SEMICOLON)
            self.got(Token.NEWL_)
        elif self.tok == Token.LIT_WORD_ and self.val == 'do':
            pass
        else:
            self.follow_err(fpos, ftok + ' foo', '`in`, `do`, `;`, or a newline')
        return wi

    def select_clause(self, s: Stmt) -> None:
        fc = ForClause(for_pos=self.pos, select=True)
        self.next()
        fc.loop = self.word_iter('select', fc.for_pos)
        fc.do_pos = self.follow_rsrv(fc.for_pos, 'select foo [in words]', 'do')
        fc.do, fc.do_last = self.follow_stmts('do', fc.do_pos, 'done')
        fc.done_pos = self.stmt_end(fc, 'select', 'done')
        s.cmd = fc

    def case_clause(self, s: Stmt) -> None:
        cc = CaseClause(case=self.pos)
        self.next()
        cc.word = self.get_word()
        if cc.word is None:
            self.follow_err(cc.case, 'case', 'a word')
        end = 'esac'
        self.got(Token.NEWL_)
        pos, ok = self.got_rsrv('{')
        if ok:
            cc.in_ = pos
            cc.braces = True
            self.check_lang(cc.pos(), LANG_MIR_BSD_KORN, '`case i {`')
            end = '}'
        else:
            cc.in_ = self.follow_rsrv(cc.case, 'case x', 'in')
        cc.items = self.case_items(end)
        cc.last, self.acc_coms = self.acc_coms, []
        cc.esac = self.stmt_end(cc, 'case', end)
        s.cmd = cc

    def case_items(self, stop: str) -> list[CaseItem]:
        items: list[CaseItem] = []
        self.got(Token.NEWL_)
        while self.tok != Token.EOF_ and not (self.tok == Token.LIT_WORD_ and self.val == stop):
            ci = CaseItem()
            ci.comments, self.acc_coms = self.acc_coms, []
            self.got(Token.LEFT_PAREN)
            while self.tok != Token.EOF_:
                w = self.get_word()
                if w is None:
                    self.cur_err('case patterns must consist of words')
                else:
                    ci.patterns.append(w)
                if self.tok == Token.RIGHT_PAREN:
                    break
                if not self.got(Token.OR):
                    self.cur_err('case patterns must be separated with %s', Token.OR)
            old = self.pre_nested(_SWITCH_CASE)
            self.next()
            ci.stmts, ci.last = self.stmt_list(stop)
            self.post_nested(old)
            if self.tok not in (Token.DBL_SEMICOLON, Token.SEMI_AND, Token.DBL_SEMI_AND, Token.SEMI_OR):
                ci.op = CaseOperator.BREAK
                items.append(ci)
                return items
            ci.last.extend(self.acc_coms)
            self.acc_coms = []
            ci.op_pos = self.pos
            ci.op = CaseOperator(self.tok)
            self.next()
            self.got(Token.NEWL_)

            # Split comments
            split = len(self.acc_coms)
            for i in range(len(self.acc_coms) - 1, -1, -1):
                c = self.acc_coms[i]
                if c.pos().col() != self.pos.col():
                    break
                split = i
            ci.comments.extend(self.acc_coms[:split])
            self.acc_coms = self.acc_coms[split:]

            items.append(ci)
        return items

    def test_clause(self, s: Stmt) -> None:
        tc = TestClause(left=self.pos)
        old = self.pre_nested(_TEST_EXPR)
        self.next()
        tc.x = self.test_expr_binary(False)
        if tc.x is None:
            self.follow_err_exp(tc.left, Token.DBL_LEFT_BRACK)
        tc.right = self.pos
        _, ok = self.got_rsrv(']]')
        if not ok:
            self.matching_err(tc.left, Token.DBL_LEFT_BRACK, Token.DBL_RIGHT_BRACK)
        self.post_nested(old)
        s.cmd = tc

    def test_expr_binary(self, past_and_or: bool) -> TestExpr | None:
        self.got(Token.NEWL_)
        if past_and_or:
            left = self.test_expr_unary()
        else:
            left = self.test_expr_binary(True)
        if left is None:
            return left
        self.got(Token.NEWL_)
        if self.tok in (Token.AND_AND, Token.OR_OR):
            pass
        elif self.tok == Token.LIT_WORD_:
            if self.val == ']]':
                return left
            op = test_binary_op(self.val)
            if op is None:
                self.cur_err('not a valid test operator: %s', self.val)
            else:
                self.tok = Token(op.value)
        elif self.tok in (Token.RDR_IN, Token.RDR_OUT):
            pass
        elif self.tok in (Token.EOF_, Token.RIGHT_PAREN):
            return left
        elif self.tok == Token.LIT_:
            self.cur_err('test operator words must consist of a single literal')
        else:
            self.cur_err('not a valid test operator: %s', self.tok)
        b = BinaryTest(
            op_pos=self.pos,
            op=BinTestOperator(self.tok),
            x=left,
        )
        if b.op in (BinTestOperator.AND_TEST, BinTestOperator.OR_TEST):
            self.next()
            b.y = self.test_expr_binary(False)
            if b.y is None:
                self.follow_err_exp(b.op_pos, b.op)
        elif b.op == BinTestOperator.TS_RE_MATCH:
            self.check_lang(self.pos, LANG_BASH_LIKE | LANG_ZSH, 'regex tests')
            self.rx_open_parens = 0
            self.rx_first_part = True
            self.quote = _TEST_EXPR_REGEXP
            # fallthrough to default
            if not isinstance(b.x, Word):
                self.pos_err(b.op_pos, 'expected %s, %s or %s after complex expr',
                             BinTestOperator.AND_TEST, BinTestOperator.OR_TEST, Token.DBL_RIGHT_BRACK)
            self.next()
            b.y = self.follow_word_tok(Token(b.op.value), b.op_pos)
        else:
            if not isinstance(b.x, Word):
                self.pos_err(b.op_pos, 'expected %s, %s or %s after complex expr',
                             BinTestOperator.AND_TEST, BinTestOperator.OR_TEST, Token.DBL_RIGHT_BRACK)
            self.next()
            b.y = self.follow_word_tok(Token(b.op.value), b.op_pos)
        return b

    def test_expr_unary(self) -> TestExpr | None:
        from .lexer import test_unary_op

        if self.tok in (Token.EOF_, Token.RIGHT_PAREN):
            return None
        if self.tok == Token.LIT_WORD_:
            op = test_unary_op(self.val)
            if op is not None:
                if op in (UnTestOperator.TS_REF_VAR, UnTestOperator.TS_MODIF):
                    if lang_in(self.lang, LANG_BASH_LIKE):
                        self.tok = Token(op.value)
                else:
                    self.tok = Token(op.value)
        if self.tok == Token.EXCL_MARK:
            u = UnaryTest(op_pos=self.pos, op=UnTestOperator.TS_NOT)
            self.next()
            u.x = self.test_expr_binary(False)
            if u.x is None:
                self.follow_err_exp(u.op_pos, u.op)
            return u
        elif self.tok in (
            Token.TS_EXISTS, Token.TS_REG_FILE, Token.TS_DIRECT,
            Token.TS_CHAR_SP, Token.TS_BLCK_SP, Token.TS_NM_PIPE,
            Token.TS_SOCKET, Token.TS_SMB_LINK, Token.TS_STICKY,
            Token.TS_GID_SET, Token.TS_UID_SET, Token.TS_GRP_OWN,
            Token.TS_USR_OWN, Token.TS_MODIF, Token.TS_READ,
            Token.TS_WRITE, Token.TS_EXEC, Token.TS_NO_EMPTY,
            Token.TS_FD_TERM, Token.TS_EMP_STR, Token.TS_NEMP_STR,
            Token.TS_OPT_SET, Token.TS_VAR_SET, Token.TS_REF_VAR,
        ):
            u = UnaryTest(op_pos=self.pos, op=UnTestOperator(self.tok))
            self.next()
            u.x = self.follow_word_tok(Token(u.op.value), u.op_pos)
            return u
        elif self.tok == Token.LEFT_PAREN:
            pe = ParenTest(lparen=self.pos)
            self.next()
            pe.x = self.test_expr_binary(False)
            if pe.x is None:
                self.follow_err_exp(pe.lparen, Token.LEFT_PAREN)
            pe.rparen = self.matched(pe.lparen, Token.LEFT_PAREN, Token.RIGHT_PAREN)
            return pe
        elif self.tok == Token.LIT_WORD_:
            if self.val == ']]':
                return None
            # fallthrough to default
            w = self.get_word()
            if w is not None:
                return w
            return None
        else:
            w = self.get_word()
            if w is not None:
                return w
            return None

    def decl_clause(self, s: Stmt) -> None:
        ds = DeclClause(variant=self.lit(self.pos, self.val))
        self.next()
        while not self.stop_token() and not self.peek_redir():
            if self.has_valid_ident():
                ds.args.append(self.get_assign(False))
            elif self.eql_offs > 0 and '{' not in self.val[:self.eql_offs]:
                self.cur_err('invalid var name')
            elif self.tok == Token.LIT_WORD_ and valid_name(self.val):
                ds.args.append(Assign(naked=True, name=self.get_lit()))
            else:
                w = self.get_word()
                if w is not None:
                    ds.args.append(Assign(naked=True, value=w))
                else:
                    self.follow_err(self.pos, ds.variant.value, 'names or assignments')
        s.cmd = ds

    def _is_bash_compound_command(self, tok: Token, val: str) -> bool:
        if tok in (Token.LEFT_PAREN, Token.DBL_LEFT_PAREN):
            return True
        if tok == Token.LIT_WORD_:
            return val in (
                '{', 'if', 'while', 'until', 'for', 'case', '[[',
                'coproc', 'let', 'function', 'declare', 'local',
                'export', 'readonly', 'typeset', 'nameref',
            )
        return False

    def time_clause(self, s: Stmt) -> None:
        tc = TimeClause(time=self.pos)
        self.next()
        _, ok = self.got_rsrv('-p')
        if ok:
            tc.posix_format = True
        tc.stmt = self.got_stmt_pipe(Stmt(position=self.pos), False)
        s.cmd = tc

    def coproc_clause(self, s: Stmt) -> None:
        cc = CoprocClause(coproc=self.pos)
        self.next()
        if self._is_bash_compound_command(self.tok, self.val):
            cc.stmt = self.got_stmt_pipe(Stmt(position=self.pos), False)
            s.cmd = cc
            return
        cc.name = self.get_word()
        cc.stmt = self.got_stmt_pipe(Stmt(position=self.pos), False)
        if cc.stmt is None:
            if cc.name is None:
                self.pos_err(cc.coproc, 'coproc clause requires a command')
                return
            cc.stmt = Stmt(position=cc.name.pos())
            cc.stmt.cmd = self.call(cc.name)
            cc.name = None
        elif cc.name is not None:
            if isinstance(cc.stmt.cmd, CallExpr):
                cc.stmt.cmd.args.insert(0, cc.name)
                cc.name = None
        s.cmd = cc

    def let_clause(self, s: Stmt) -> None:
        from .parser_arithm import arithm_expr as _arithm_expr

        lc = LetClause(let=self.pos)
        old = self.pre_nested(_ARITHM_EXPR_LET)
        self.next()
        while not self.stop_token() and not self.peek_redir():
            x = _arithm_expr(self, True)
            if x is None:
                break
            lc.exprs.append(x)
        if len(lc.exprs) == 0:
            self.follow_err_exp(lc.let, 'let')
        self.post_nested(old)
        s.cmd = lc

    def bash_func_decl(self, s: Stmt) -> None:
        fpos = self.pos
        self.next()
        names: list[Lit] = []
        while self.tok == Token.LIT_WORD_ and self.val != '{':
            names.append(self.lit(self.pos, self.val))
            self.next()
        has_parens = self.got(Token.LEFT_PAREN)
        if len(names) == 0:
            if has_parens or (self.tok == Token.LIT_WORD_ and self.val == '{'):
                self.check_lang(fpos, LANG_ZSH, 'anonymous functions')
            elif not lang_in(self.lang, LANG_ZSH):
                self.follow_err(fpos, 'function', 'a name')
            names = []
        elif len(names) == 1:
            pass  # allowed in all variants
        else:
            self.check_lang(fpos, LANG_ZSH, 'multi-name functions')
        if has_parens:
            self.follow(fpos, 'function foo(', Token.RIGHT_PAREN)
        self.func_decl(s, fpos, True, has_parens, names)

    def test_decl(self, s: Stmt) -> None:
        td = TestDecl(position=self.pos)
        self.next()
        td.description = self.get_word()
        if td.description is None:
            self.follow_err(td.position, '@test', 'a description word')
        td.body = self.get_stmt(False, False, True)
        if td.body is None:
            self.follow_err(td.position, '@test "desc"', 'a statement')
        s.cmd = td

    def call_expr(self, s: Stmt, w: Word | None, assign: bool) -> None:
        ce = self.call(w)
        if w is None:
            ce.args = []
        if assign:
            ce.assigns.append(self.get_assign(True))
        while True:
            if self.tok in (
                Token.EOF_, Token.NEWL_, Token.SEMICOLON, Token.AND, Token.OR,
                Token.AND_AND, Token.OR_OR, Token.OR_AND,
                Token.DBL_SEMICOLON, Token.SEMI_AND, Token.DBL_SEMI_AND, Token.SEMI_OR,
            ):
                break
            elif self.tok == Token.LIT_WORD_:
                if len(ce.args) == 0 and self.has_valid_ident():
                    ce.assigns.append(self.get_assign(True))
                else:
                    if self.val == '{' and w is not None and w.lit() == 'function':
                        self.check_lang(self.pos, LANG_BASH_LIKE, 'the "function" builtin')
                    if lang_in(self.lang, LANG_ZSH) and self.val == '}':
                        break
                    ce.args.append(self.word_one(self.lit(self.pos, self.val)))
                    self.next()
            elif self.tok == Token.LIT_:
                if len(ce.args) == 0 and self.has_valid_ident():
                    ce.assigns.append(self.get_assign(True))
                else:
                    ce.args.append(self.word_any_number())
            elif (
                (cond_bck3 := (self.tok == Token.BCK_QUOTE))
                or (cond_exp3 := (self.tok in (  # noqa: F841
                    Token.DOLL_BRACE, Token.DOLL_DBL_PAREN, Token.DOLL_PAREN,
                    Token.DOLLAR, Token.CMD_IN, Token.ASSGN_PAREN, Token.CMD_OUT,
                    Token.SGL_QUOTE, Token.DOLL_SGL_QUOTE,
                    Token.DBL_QUOTE, Token.DOLL_DBL_QUOTE, Token.DOLL_BRACK,
                    Token.GLOB_QUEST, Token.GLOB_STAR, Token.GLOB_PLUS,
                    Token.GLOB_AT, Token.GLOB_EXCL,
                )))
            ):
                if cond_bck3:
                    if self.backquote_end():
                        break
                    cond_exp3 = True  # fallthrough
                if cond_exp3:  # noqa: F821
                    ce.args.append(self.word_any_number())
            elif self.tok == Token.DBL_LEFT_PAREN:
                self.cur_err('%s can only be used to open an arithmetic cmd', self.tok)
            elif (
                (cond_rp := (self.tok == Token.RIGHT_PAREN))
                or (cond_def3 := True)  # noqa: F841
            ):
                if cond_rp:
                    if self.quote == _SUB_CMD:
                        break
                    # fallthrough to default
                if self.peek_redir():
                    self.do_redirect(s)
                    continue
                if len(ce.args) > 0:
                    cmd = ce.args[0].lit() if hasattr(ce.args[0], 'lit') else None
                    if cmd and self._is_bash_compound_command(Token.LIT_WORD_, cmd):
                        self.check_lang(self.pos, LANG_BASH_LIKE, 'the %s builtin', cmd)
                self.cur_err('a command can only contain words and redirects; encountered %s', self.tok)
        if len(ce.args) == 0:
            ce.args = []
        else:
            for asgn in ce.assigns:
                if asgn.index is not None or asgn.array is not None:
                    self.pos_err(asgn.pos(), 'inline variables cannot be arrays')
        s.cmd = ce

    def func_decl(
            self,
            s: Stmt,
            pos: Pos,
            long: bool,
            with_parens: bool,
            names: list[Lit] | None = None,
    ) -> None:
        fd = FuncDecl(
            position=pos,
            rsrv_word=long,
            parens=with_parens,
        )
        if names is not None and len(names) == 1:
            fd.name = names[0]
        else:
            fd.names = names or []
        self.got(Token.NEWL_)
        fd.body = self.get_stmt(False, False, True)
        if fd.body is None:
            self.follow_err(fd.pos(), 'foo()', 'a statement')
        s.cmd = fd
