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
import typing as ta

from omlish import lang

from .langs import LANG_BASH_LIKE
from .langs import LANG_MIR_BSD_KORN
from .langs import LANG_ZSH
from .langs import lang_in
from .tokens import BinTestOperator
from .tokens import Token
from .tokens import UnTestOperator


with lang.auto_proxy_import(globals()):
    from . import parser


##


# Sentinel rune values. In the Go original these are utf8.RuneSelf (0x80) and utf8.RuneSelf+1.
# In Python we use Unicode noncharacters that cannot appear in valid shell source.
_EOF_RUNE = '\uffff'   # signals end of input (replaces utf8.RuneSelf)
_ESC_NEWL = '\ufffe'   # escaped newline pseudo-rune (replaces escNewl)


##


def ascii_letter(r: str) -> bool:
    return ('a' <= r <= 'z') or ('A' <= r <= 'Z')


def ascii_digit(r: str) -> bool:
    return '0' <= r <= '9'


# bytes that form or start a token
def reg_ops(r: str) -> bool:
    if r in (';', '"', '\'', '(', ')', '$', '|', '&', '>', '<', '`'):
        return True
    return False


# tokenize these inside parameter expansions
def param_ops(r: str) -> bool:
    if r in ('}', '#', '!', ':', '-', '+', '=', '?', '%', '[', ']', '/', '^', ',', '@', '*'):
        return True
    return False


# tokenize these inside arithmetic expansions
def arithm_ops(r: str) -> bool:
    if r in ('+', '-', '!', '~', '*', '/', '%', '(', ')', '^', '<', '>', ':', '=', ',', '?', '|', '&', '[', ']', '#', '.'):  # noqa
        return True
    return False


def bquote_escaped(b: str) -> bool:
    if b in ('$', '`', '\\'):
        return True
    return False


r"""
TODO: original go for parser_rune / parser_fill (byte-level IO, not applicable to string-based Python parser):

const escNewl rune = utf8.RuneSelf + 1


def parser_rune(p: 'parser.Parser') -> str:
    if p.r == '\n' or p.r == escNewl {
        # p.r instead of b so that newline
        # character positions don't have col 0.
        p.line++
        p.col = 0

    p.col += int64(p.w)
    bquotes := 0

retry:
    if p.bsp >= uint(len(p.bs)) and p.fill() == 0 {
        if len(p.bs) == 0 {
            # Necessary for the last position to be correct.
            # TODO: this is not exactly intuitive; figure out a better way.
            p.bsp = 1

        p.r = utf8.RuneSelf
        p.w = 1
        return p.r

    if b := p.bs[p.bsp]; b < utf8.RuneSelf {
        p.bsp++
        switch b {
        case '\x00':
            # Ignore null bytes while parsing, like bash.
            p.col++
            goto retry

        case '\r':
            if p.peek() == '\n' { # \r\n turns into \n
                p.col++
                goto retry

        case '\\':
            if p.r == '\\' {
            else if p.peek() == '\n' {
                p.bsp++
                p.w, p.r = 1, escNewl
                return escNewl
            else if p1, p2 := p.peekTwo(); p1 == '\r' and p2 == '\n' { # \\\r\n turns into \\\n
                p.col++
                p.bsp += 2
                p.w, p.r = 2, escNewl
                return escNewl

            # TODO: why is this necessary to ensure correct position info?
            p.readEOF = False
            if p.openBquotes > 0 and bquotes < p.openBquotes and
                p.bsp < uint(len(p.bs)) and bquote_escaped(p.bs[p.bsp]) {
                # We turn backquote command substitutions into $(),
                # so we remove the extra backslashes needed by the backquotes.
                bquotes++
                p.col++
                goto retry

        if b == '`' {
            p.lastBquoteEsc = bquotes
        if p.litBs is not None {
            p.litBs = append(p.litBs, b)
        p.w, p.r = 1, rune(b)
        return p.r

decodeRune:
    var w int
    p.r, w = utf8.DecodeRune(p.bs[p.bsp:])
    if p.r == utf8.RuneError and not utf8.FullRune(p.bs[p.bsp:]) {
        # we need more bytes to read a full non-ascii rune
        if p.fill() > 0 {
            goto decodeRune

    if p.litBs is not None {
        p.litBs = append(p.litBs, p.bs[p.bsp:p.bsp+uint(w)]...)

    p.bsp += uint(w)
    if p.r == utf8.RuneError and w == 1 {
        p.posErr(p.nextPos(), "invalid UTF-8 encoding")

    p.w = w
    return p.r

# fill reads more bytes from the input src into readBuf.
# Any bytes that had not yet been used at the end of the buffer
# are slid into the beginning of the buffer.
# The number of read bytes is returned, which is at least one
# unless a read error occurred, such as [io.EOF].
def parser_fill(p: 'parser.Parser', n: int) -> None:
    if p.readEOF or p.r == utf8.RuneSelf {
        # If the reader already gave us [io.EOF], do not try again.
        # If we decided to stop for any reason, do not bother reading either.
        return 0

    p.offs += int64(p.bsp)
    left := len(p.bs) - int(p.bsp)
    copy(p.readBuf[:left], p.readBuf[p.bsp:])

readAgain:
    n, err := 0, p.readErr
    if err == nil {
        n, err = p.src.Read(p.readBuf[left:])
        p.readErr = err
        if err == io.EOF {
            p.readEOF = True

    if n == 0 {
        if err == nil {
            goto readAgain

        # don't use p.errPass as we don't want to overwrite p.tok
        if err != io.EOF {
            p.err = err

        if left > 0 {
            p.bs = p.readBuf[:left]
        else {
            p.bs = nil

    else {
        p.bs = p.readBuf[:left+n]

    p.bsp = 0
    return n
"""  # noqa


def next_keep_spaces(p: 'parser.Parser') -> None:
    r = p.r
    if p.quote != p._HDOC_BODY and p.quote != p._HDOC_BODY_TABS:
        # Heredocs handle escaped newlines in a special way, but others do not.
        while r == _ESC_NEWL:
            r = p.rune()

    p.pos = p.next_pos()
    if p.quote == p._RUNE_BY_RUNE:
        p.tok = Token.ILLEGAL_TOK
    elif p.quote == p._DBL_QUOTES:
        if r in ('`', '"', '$'):
            p.tok = dq_token(p, r)
        else:
            advance_lit_dquote(p, r)
    elif p.quote in (p._HDOC_BODY, p._HDOC_BODY_TABS):
        if r in ('`', '$'):
            p.tok = dq_token(p, r)
        else:
            advance_lit_hdoc(p, r)
    elif (
        (cond_repl := (p.quote == p._PARAM_EXP_REPL))
        or (cond_exp := (p.quote == p._PARAM_EXP_EXP))  # noqa: F841
    ):
        if cond_repl:
            if r == '/':
                p.rune()
                p.tok = Token.SLASH
            else:
                # fallthrough to paramExpExp handling
                cond_exp = True
        if cond_exp:  # noqa: F821
            if r == '}':
                p.tok = param_token(p, r)
            elif r in ('`', '"', '$', '\''):
                p.tok = reg_token(p, r)
            else:
                advance_lit_other(p, r)

    if p.err is not None:
        p.tok = Token.EOF_


def next_(p: 'parser.Parser') -> None:
    if p.r == _EOF_RUNE:
        p.tok = Token.EOF_
        return

    p.spaced = False
    if p.quote & p._ALL_KEEP_SPACES != 0:
        next_keep_spaces(p)
        return

    r = p.r
    while r == _ESC_NEWL:
        r = p.rune()

    # skipSpace
    while True:
        if r == _EOF_RUNE:
            p.tok = Token.EOF_
            return
        elif r == _ESC_NEWL:
            r = p.rune()
        elif r in (' ', '\t', '\r'):
            p.spaced = True
            r = p.rune()
        elif r == '\n':
            if p.tok == Token.NEWL_:
                # merge consecutive newline tokens
                r = p.rune()
                continue

            p.spaced = True
            p.tok = Token.NEWL_
            if p.quote != p._HDOC_WORD and len(p.heredocs) > p.buried_hdocs:
                p.do_heredocs()

            return
        else:
            break

    if p.stop_at is not None and (p.spaced or p.tok == Token.ILLEGAL_TOK or p.stop_token()):
        if p.src[p.bsp - 1:].startswith(p.stop_at):
            p.r = _EOF_RUNE
            p.w = 1
            p.tok = Token.EOF_
            return

    p.pos = p.next_pos()
    if p.quote & p._ALL_REG_TOKENS != 0:
        if r in (';', '"', '\'', '(', ')', '$', '|', '&', '>', '<', '`'):
            if r == '<' and lang_in(p.lang, LANG_ZSH) and zsh_num_range(p):
                advance_lit_none(p, r)
                return
            p.tok = reg_token(p, r)
        elif r == '#':
            # If we're parsing $foo#bar, ${foo}#bar, 'foo'#bar, or "foo"#bar,
            # #bar is a continuation of the same word, not a comment.
            if p.quote == p._UNQUOTED_WORD_CONT and not p.spaced:
                advance_lit_none(p, r)
                return
            r = p.rune()
            new_lit(p, r)
            while True:
                if r in ('\n', _EOF_RUNE):
                    break
                elif r == _ESC_NEWL:
                    p.lit_bs.append('\\')
                    p.lit_bs.append('\n')
                    break
                elif r == '`':
                    if p.backquote_end():
                        break
                r = p.rune()
            if p.keep_comments:
                p.cur_coms.append(p._comment(
                    hash_pos=p.pos,
                    text=end_lit(p),
                ))
            else:
                p.lit_bs = None
            next_(p)
        elif r == '[':
            if p.quote == p._ARRAY_ELEMS:
                p.rune()
                p.tok = Token.LEFT_BRACK
            else:
                advance_lit_none(p, r)
        elif r == '=':
            if p.peek() == '(':
                p.rune()
                p.rune()
                p.tok = Token.ASSGN_PAREN
            elif p.quote == p._ARRAY_ELEMS:
                p.rune()
                p.tok = Token.ASSGN
            else:
                advance_lit_none(p, r)
        elif r in ('?', '*', '+', '@', '!'):
            if extended_glob(p):
                if r == '?':
                    p.tok = Token.GLOB_QUEST
                elif r == '*':
                    p.tok = Token.GLOB_STAR
                elif r == '+':
                    p.tok = Token.GLOB_PLUS
                elif r == '@':
                    p.tok = Token.GLOB_AT
                elif r == '!':
                    p.tok = Token.GLOB_EXCL
                p.rune()
                p.rune()
            else:
                advance_lit_none(p, r)
        else:
            advance_lit_none(p, r)
    elif p.quote & p._ALL_ARITHM_EXPR != 0 and arithm_ops(r):
        p.tok = arithm_token(p, r)
    elif p.quote & p._ALL_PARAM_EXP != 0 and param_ops(r):
        p.tok = param_token(p, r)
    elif p.quote == p._TEST_EXPR_REGEXP:
        if not p.rx_first_part and p.spaced:
            p.quote = p._TEST_EXPR
            # re-enter skipSpace logic via recursion
            next_(p)
            return
        p.rx_first_part = False
        if r in (';', '"', '\'', '$', '&', '>', '<', '`'):
            p.tok = reg_token(p, r)
        elif r == ')':
            if p.rx_open_parens > 0:
                # continuation of open paren
                advance_lit_re(p, r)
            else:
                p.tok = Token.RIGHT_PAREN
                p.quote = p._TEST_EXPR
                p.rune()  # we are tokenizing manually
        else:  # including '(', '|'
            advance_lit_re(p, r)
    elif reg_ops(r):
        p.tok = reg_token(p, r)
    else:
        advance_lit_other(p, r)
    if p.err is not None:
        p.tok = Token.EOF_


# extended_glob determines whether we're parsing a Bash extended globbing expression.
# For example, whether `*` or `@` are followed by `(` to form `@(foo)`.
def extended_glob(p: 'parser.Parser') -> bool:
    if lang_in(p.lang, LANG_ZSH):
        # Zsh doesn't have extended globs like bash/mksh.
        # We still tokenize +( @( !( so the parser can give a clear error,
        # but not *( or ?( as those are used in zsh glob qualifiers.
        if p.r not in ('+', '@', '!'):
            return False
    if p.val == 'function':
        # We don't support e.g. `function @() { ... }` at the moment, but we could.
        return False
    if p.peek() == '(':
        # NOTE: empty pattern list is a valid globbing syntax like `@()`,
        # but we'll operate on the "likelihood" that it is a function;
        # only tokenize if its a non-empty pattern list.
        # We do this after peeking for just one byte, so that the input `echo *`
        # followed by a newline does not hang an interactive shell parser until
        # another byte is input.
        _, p2 = p.peek_two()
        return p2 != ')'
    return False


def reg_token(p: 'parser.Parser', r: str) -> Token:
    if r == '\'':
        p.rune()
        return Token.SGL_QUOTE
    elif r == '"':
        p.rune()
        return Token.DBL_QUOTE
    elif r == '`':
        # Don't call p.rune, as we need to work out p.openBquotes to
        # properly handle backslashes in the lexer.
        return Token.BCK_QUOTE
    elif r == '&':
        pr = p.rune()
        if pr == '&':
            p.rune()
            return Token.AND_AND
        elif pr == '>':
            pr = p.rune()
            if pr == '|':
                p.rune()
                return Token.RDR_ALL_CLOB
            elif pr == '!':
                p.rune()
                return Token.RDR_ALL_TRUNC
            elif pr == '>':
                pr = p.rune()
                if pr == '|':
                    p.rune()
                    return Token.APP_ALL_CLOB
                elif pr == '!':
                    p.rune()
                    return Token.APP_ALL_TRUNC
                return Token.APP_ALL
            return Token.RDR_ALL
        return Token.AND
    elif r == '|':
        pr = p.rune()
        if pr == '|':
            p.rune()
            return Token.OR_OR
        elif pr == '&':
            if not lang_in(p.lang, LANG_BASH_LIKE | LANG_MIR_BSD_KORN | LANG_ZSH):
                return Token.OR
            p.rune()
            return Token.OR_AND
        return Token.OR
    elif r == '$':
        pr = p.rune()
        if pr == '\'':
            if not lang_in(p.lang, LANG_BASH_LIKE | LANG_MIR_BSD_KORN | LANG_ZSH):
                return Token.DOLLAR
            p.rune()
            return Token.DOLL_SGL_QUOTE
        elif pr == '"':
            if not lang_in(p.lang, LANG_BASH_LIKE | LANG_MIR_BSD_KORN):
                return Token.DOLLAR
            p.rune()
            return Token.DOLL_DBL_QUOTE
        elif pr == '{':
            p.rune()
            return Token.DOLL_BRACE
        elif pr == '[':
            if not lang_in(p.lang, LANG_BASH_LIKE):
                # latter to not tokenise ${$[@]} as $[
                return Token.DOLLAR
            p.rune()
            return Token.DOLL_BRACK
        elif pr == '(':
            if p.rune() == '(':
                p.rune()
                return Token.DOLL_DBL_PAREN
            return Token.DOLL_PAREN
        return Token.DOLLAR
    elif r == '(':
        if p.rune() == '(' and lang_in(p.lang, LANG_BASH_LIKE | LANG_MIR_BSD_KORN | LANG_ZSH) and p.quote != p._TEST_EXPR:  # noqa
            p.rune()
            return Token.DBL_LEFT_PAREN
        return Token.LEFT_PAREN
    elif r == ')':
        p.rune()
        return Token.RIGHT_PAREN
    elif r == ';':
        pr = p.rune()
        if pr == ';':
            if p.rune() == '&' and lang_in(p.lang, LANG_BASH_LIKE):
                p.rune()
                return Token.DBL_SEMI_AND
            return Token.DBL_SEMICOLON
        elif pr == '&':
            if not lang_in(p.lang, LANG_BASH_LIKE | LANG_MIR_BSD_KORN | LANG_ZSH):
                return Token.SEMICOLON
            p.rune()
            return Token.SEMI_AND
        elif pr == '|':
            if not lang_in(p.lang, LANG_MIR_BSD_KORN):
                return Token.SEMICOLON
            p.rune()
            return Token.SEMI_OR
        return Token.SEMICOLON
    elif r == '<':
        pr = p.rune()
        if pr == '<':
            r2 = p.rune()
            if r2 == '-':
                p.rune()
                return Token.DASH_HDOC
            elif r2 == '<':
                p.rune()
                return Token.WORD_HDOC
            return Token.HDOC
        elif pr == '>':
            p.rune()
            return Token.RDR_IN_OUT
        elif pr == '&':
            p.rune()
            return Token.DPL_IN
        elif pr == '(':
            if not lang_in(p.lang, LANG_BASH_LIKE | LANG_ZSH):
                return Token.RDR_IN
            p.rune()
            return Token.CMD_IN
        return Token.RDR_IN
    elif r == '>':
        pr = p.rune()
        if pr == '>':
            pr = p.rune()
            if pr == '|':
                p.rune()
                return Token.APP_CLOB
            elif pr == '!':
                p.rune()
                return Token.APP_TRUNC
            return Token.APP_OUT
        elif pr == '&':
            p.rune()
            return Token.DPL_OUT
        elif pr == '|':
            p.rune()
            return Token.RDR_CLOB
        elif pr == '!':
            p.rune()
            return Token.RDR_TRUNC
        elif pr == '(':
            if not lang_in(p.lang, LANG_BASH_LIKE | LANG_ZSH):
                return Token.RDR_OUT
            p.rune()
            return Token.CMD_OUT
        return Token.RDR_OUT
    raise RuntimeError('unreachable')


def dq_token(p: 'parser.Parser', r: str) -> Token:
    if r == '"':
        p.rune()
        return Token.DBL_QUOTE
    elif r == '`':
        # Don't call p.rune, as we need to work out p.openBquotes to
        # properly handle backslashes in the lexer.
        return Token.BCK_QUOTE
    elif r == '$':
        pr = p.rune()
        if pr == '{':
            p.rune()
            return Token.DOLL_BRACE
        elif pr == '[':
            if not lang_in(p.lang, LANG_BASH_LIKE):
                return Token.DOLLAR
            p.rune()
            return Token.DOLL_BRACK
        elif pr == '(':
            if p.rune() == '(':
                p.rune()
                return Token.DOLL_DBL_PAREN
            return Token.DOLL_PAREN
        return Token.DOLLAR
    raise RuntimeError('unreachable')


def param_token(p: 'parser.Parser', r: str) -> Token:
    if r == '}':
        p.rune()
        return Token.RIGHT_BRACE
    elif r == ':':
        pr = p.rune()
        if pr == '+':
            p.rune()
            return Token.COL_PLUS
        elif pr == '-':
            p.rune()
            return Token.COL_MINUS
        elif pr == '?':
            p.rune()
            return Token.COL_QUEST
        elif pr == '=':
            p.rune()
            return Token.COL_ASSGN
        elif pr == '#':
            p.rune()
            return Token.COL_HASH
        return Token.COLON
    elif r == '+':
        p.rune()
        return Token.PLUS
    elif r == '-':
        p.rune()
        return Token.MINUS
    elif r == '?':
        p.rune()
        return Token.QUEST
    elif r == '=':
        p.rune()
        return Token.ASSGN
    elif r == '%':
        if p.rune() == '%':
            p.rune()
            return Token.DBL_PERC
        return Token.PERC
    elif r == '#':
        if p.rune() == '#':
            p.rune()
            return Token.DBL_HASH
        return Token.HASH
    elif r == '!':
        p.rune()
        return Token.EXCL_MARK
    elif r == ']':
        p.rune()
        return Token.RIGHT_BRACK
    elif r == '/':
        if p.rune() == '/':
            p.rune()
            return Token.DBL_SLASH
        return Token.SLASH
    elif r == '^':
        if p.rune() == '^':
            p.rune()
            return Token.DBL_CARET
        return Token.CARET
    elif r == ',':
        if p.rune() == ',':
            p.rune()
            return Token.DBL_COMMA
        return Token.COMMA
    elif r == '@':
        p.rune()
        return Token.AT
    elif r == '*':
        p.rune()
        return Token.STAR

    # This func gets called by the parser in runeByRune mode;
    # we need to handle EOF and unexpected runes.
    elif r == _EOF_RUNE:
        return Token.EOF_
    else:
        return Token.ILLEGAL_TOK


def arithm_token(p: 'parser.Parser', r: str) -> Token:
    if r == '!':
        if p.rune() == '=':
            p.rune()
            return Token.NEQUAL
        return Token.EXCL_MARK
    elif r == '=':
        if p.rune() == '=':
            p.rune()
            return Token.EQUAL
        return Token.ASSGN
    elif r == '~':
        p.rune()
        return Token.TILDE
    elif r == '(':
        p.rune()
        return Token.LEFT_PAREN
    elif r == ')':
        p.rune()
        return Token.RIGHT_PAREN
    elif r == '&':
        pr = p.rune()
        if pr == '&':
            if p.rune() == '=' and lang_in(p.lang, LANG_ZSH):
                p.rune()
                return Token.AND_BOOL_ASSGN
            return Token.AND_AND
        elif pr == '=':
            p.rune()
            return Token.AND_ASSGN
        return Token.AND
    elif r == '|':
        pr = p.rune()
        if pr == '|':
            if p.rune() == '=' and lang_in(p.lang, LANG_ZSH):
                p.rune()
                return Token.OR_BOOL_ASSGN
            return Token.OR_OR
        elif pr == '=':
            p.rune()
            return Token.OR_ASSGN
        return Token.OR
    elif r == '<':
        pr = p.rune()
        if pr == '<':
            if p.rune() == '=':
                p.rune()
                return Token.SHL_ASSGN
            return Token.HDOC
        elif pr == '=':
            p.rune()
            return Token.LEQUAL
        return Token.RDR_IN
    elif r == '>':
        pr = p.rune()
        if pr == '>':
            if p.rune() == '=':
                p.rune()
                return Token.SHR_ASSGN
            return Token.APP_OUT
        elif pr == '=':
            p.rune()
            return Token.GEQUAL
        return Token.RDR_OUT
    elif r == '+':
        pr = p.rune()
        if pr == '+':
            p.rune()
            return Token.ADD_ADD
        elif pr == '=':
            p.rune()
            return Token.ADD_ASSGN
        return Token.PLUS
    elif r == '-':
        pr = p.rune()
        if pr == '-':
            p.rune()
            return Token.SUB_SUB
        elif pr == '=':
            p.rune()
            return Token.SUB_ASSGN
        return Token.MINUS
    elif r == '%':
        if p.rune() == '=':
            p.rune()
            return Token.REM_ASSGN
        return Token.PERC
    elif r == '*':
        pr = p.rune()
        if pr == '*':
            if p.rune() == '=' and lang_in(p.lang, LANG_ZSH):
                p.rune()
                return Token.POW_ASSGN
            return Token.POWER
        elif pr == '=':
            p.rune()
            return Token.MUL_ASSGN
        return Token.STAR
    elif r == '/':
        if p.rune() == '=':
            p.rune()
            return Token.QUO_ASSGN
        return Token.SLASH
    elif r == '^':
        pr = p.rune()
        if pr == '^':
            if p.rune() == '=' and lang_in(p.lang, LANG_ZSH):
                p.rune()
                return Token.XOR_BOOL_ASSGN
            return Token.DBL_CARET
        elif pr == '=':
            p.rune()
            return Token.XOR_ASSGN
        return Token.CARET
    elif r == '[':
        p.rune()
        return Token.LEFT_BRACK
    elif r == ']':
        p.rune()
        return Token.RIGHT_BRACK
    elif r == ',':
        p.rune()
        return Token.COMMA
    elif r == '?':
        p.rune()
        return Token.QUEST
    elif r == ':':
        p.rune()
        return Token.COLON
    elif r == '#':
        p.rune()
        return Token.HASH
    elif r == '.':
        p.rune()
        return Token.PERIOD
    raise RuntimeError('unreachable')


##


def new_lit(p: 'parser.Parser', r: str) -> None:
    if r != _EOF_RUNE and r != _ESC_NEWL:
        p.lit_bs = [r]
    else:
        p.lit_bs = []


def end_lit(p: 'parser.Parser') -> str:
    if p.r == _EOF_RUNE or p.r == _ESC_NEWL:
        s = ''.join(p.lit_bs)
    else:
        # exclude the last rune which hasn't been consumed yet
        s = ''.join(p.lit_bs[:-1]) if p.lit_bs else ''
    p.lit_bs = None
    return s


def is_lit_redir(p: 'parser.Parser') -> bool:
    lit = p.lit_bs[:-1] if p.lit_bs else []
    if not lit:
        return False
    lit_str = ''.join(lit)
    if lit_str[0] == '{' and lit_str[-1] == '}':
        return parser.valid_name(lit_str[1:-1])
    return _number_literal(lit_str)


def single_rune_param(r: str) -> bool:
    if r in ('@', '*', '#', '$', '?', '!', '-', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9'):
        return True
    return False


def param_name_rune(r: str) -> bool:
    return ascii_letter(r) or ascii_digit(r) or r == '_'


def _number_literal(val: str) -> bool:
    if len(val) == 0:
        return False
    for r in val:
        if not ascii_digit(r):
            return False
    return True


def advance_lit_other(p: 'parser.Parser', r: str) -> None:
    tok = Token.LIT_WORD_
    new_lit(p, r)
    while r != _EOF_RUNE:
        if r == '\\':  # escaped byte follows
            p.rune()
        elif r in ('\'', '"', '`', '$'):
            tok = Token.LIT_
            break
        elif r == '}':
            if p.quote & p._ALL_PARAM_EXP != 0:
                break
        elif r == '/':
            if p.quote != p._PARAM_EXP_EXP:
                break
        elif r in (':', '=', '%', '^', ',', '?', '!', '~', '*'):
            if p.quote & p._ALL_ARITHM_EXPR != 0:
                break
        elif r == '.':
            if not lang_in(p.lang, LANG_ZSH) and p.quote & p._ALL_ARITHM_EXPR != 0:
                break
        elif r in ('[', ']'):
            if (
                lang_in(p.lang, LANG_BASH_LIKE | LANG_MIR_BSD_KORN | LANG_ZSH)
                and p.quote & p._ALL_ARITHM_EXPR != 0
            ):
                break
            # fallthrough to the + - space etc case
            if p.quote & p._ALL_KEEP_SPACES == 0:
                break
        elif r in ('+', '-', ' ', '\t', ';', '&', '>', '<', '|', '(', ')', '\n', '\r'):
            if p.quote & p._ALL_KEEP_SPACES == 0:
                break
        r = p.rune()
    p.tok, p.val = tok, end_lit(p)


# litBsGlob reports whether the literal bytes accumulated so far
# contain a glob metacharacter, excluding the last byte which is '('.
def lit_bs_glob(p: 'parser.Parser') -> bool:
    # Exclude the last byte which is the '(' that triggered this check.
    for b in (p.lit_bs[:-1] if p.lit_bs else []):
        if b in ('*', '?', '['):
            return True
        elif b == '/':
            # Paths like /bin/sh(:t) can also have glob qualifiers;
            # function names never contain slashes.
            return True
    return False


# zshNumRange peeks at the bytes after '<' to check for a zsh numeric
# range glob pattern like <->, <5->, <-10>, or <5-10>.
def zsh_num_range(p: 'parser.Parser') -> bool:
    # Peeking a handful of bytes here should be enough.
    rest = p.src[p.bsp:]
    i = 0
    while i < len(rest) and '0' <= rest[i] <= '9':
        i += 1
    if i >= len(rest) or rest[i] != '-':
        return False
    i += 1
    while i < len(rest) and '0' <= rest[i] <= '9':
        i += 1
    return i < len(rest) and rest[i] == '>'


def advance_lit_none(p: 'parser.Parser', r: str) -> None:
    p.eql_offs = -1
    tok = Token.LIT_WORD_
    new_lit(p, r)
    while r != _EOF_RUNE:
        if r in (' ', '\t', '\n', '\r', '&', '|', ';', ')'):
            break
        elif r == '(':
            if lang_in(p.lang, LANG_ZSH) and lit_bs_glob(p):
                # Zsh glob qualifiers like *(.), **(/) or *(om[1,5]); consume until ')'.
                while True:
                    r = p.rune()
                    if r == _EOF_RUNE or r == ')':
                        break
                r = p.rune()
                continue
            break
        elif r == '\\':  # escaped byte follows
            p.rune()
        elif r in ('>', '<'):
            if r == '<' and lang_in(p.lang, LANG_ZSH) and zsh_num_range(p):
                # Zsh numeric range glob like <-> or <1-100>; consume until '>'.
                while True:
                    r = p.rune()
                    if r == '>' or r == _EOF_RUNE:
                        break
                r = p.rune()
                continue
            if p.peek() == '(':
                tok = Token.LIT_
            elif is_lit_redir(p):
                tok = Token.LIT_REDIR_
            break
        elif r == '`':
            if p.quote != p._SUB_CMD_BCKQUO:
                tok = Token.LIT_
            break
        elif r in ('"', '\'', '$'):
            tok = Token.LIT_
            break
        elif r in ('?', '*', '+', '@', '!'):
            if extended_glob(p):
                tok = Token.LIT_
                break
        elif r == '=':
            if p.eql_offs < 0:
                p.eql_offs = len(p.lit_bs) - 1
        elif r == '[':
            if (
                lang_in(p.lang, LANG_BASH_LIKE | LANG_MIR_BSD_KORN | LANG_ZSH)
                and len(p.lit_bs) > 1
                and p.lit_bs[0] != '['
            ):
                tok = Token.LIT_
                break
        r = p.rune()
    p.tok, p.val = tok, end_lit(p)


def advance_lit_dquote(p: 'parser.Parser', r: str) -> None:
    tok = Token.LIT_WORD_
    new_lit(p, r)
    while r != _EOF_RUNE:
        if r == '"':
            break
        elif r == '\\':  # escaped byte follows
            p.rune()
        elif r in (_ESC_NEWL, '`', '$'):
            tok = Token.LIT_
            break
        r = p.rune()
    p.tok, p.val = tok, end_lit(p)


def advance_lit_hdoc(p: 'parser.Parser', r: str) -> None:
    # Unlike the rest of nextKeepSpaces quote states, we handle escaped
    # newlines here. If lastTok==_Lit, then we know we're following an
    # escaped newline, so the first line can't end the heredoc.
    last_tok = p.tok
    while r == _ESC_NEWL:
        r = p.rune()
        last_tok = Token.LIT_
    p.pos = p.next_pos()

    p.tok = Token.LIT_
    new_lit(p, r)
    while p.quote == p._HDOC_BODY_TABS and r == '\t':
        r = p.rune()
    l_start = len(p.lit_bs) - 1
    stop = p.hdoc_stops[-1]
    while True:
        if r in (_ESC_NEWL, '$'):
            p.val = end_lit(p)
            return
        elif r == '\\':  # escaped byte follows
            p.rune()
        elif (
            (cond_bck := (r == '`'))
            or (cond_nl := (r in ('\n', _EOF_RUNE)))  # noqa: F841
        ):
            if cond_bck:
                if not p.backquote_end():
                    p.val = end_lit(p)
                    return
                cond_nl = True
            if cond_nl:  # noqa: F821
                if p.parsing_doc:
                    if r == _EOF_RUNE:
                        p.tok = Token.LIT_WORD_
                        p.val = end_lit(p)
                        return
                elif l_start == 0 and last_tok == Token.LIT_:
                    # This line starts right after an escaped
                    # newline, so it should never end the heredoc.
                    pass
                elif l_start >= 0:
                    # Compare the current line with the stop word.
                    line = p.lit_bs[l_start:]
                    if r != _EOF_RUNE and len(line) > 0:
                        line = line[:-1]  # minus trailing character
                    line_str = ''.join(line)
                    if line_str == stop:
                        p.tok = Token.LIT_WORD_
                        full = end_lit(p)
                        p.val = full[:l_start]
                        if p.val == '':
                            p.tok = Token.NEWL_
                        p.hdoc_stops[-1] = None
                        return
                if r != '\n':
                    return  # hit an unexpected EOF or closing backquote
                while p.quote == p._HDOC_BODY_TABS and p.peek() == '\t':
                    p.rune()
                l_start = len(p.lit_bs)
        r = p.rune()


def quoted_hdoc_word(p: 'parser.Parser') -> ta.Any:  # -> Word | None
    r = p.r
    new_lit(p, r)
    pos = p.next_pos()
    stop = p.hdoc_stops[-1]
    while True:
        if r == _EOF_RUNE:
            return None
        while p.quote == p._HDOC_BODY_TABS and r == '\t':
            r = p.rune()
        l_start = len(p.lit_bs) - 1
        while True:
            if r in (_EOF_RUNE, '\n'):
                break
            elif r == '`':
                if p.backquote_end():
                    break
            elif r == _ESC_NEWL:
                p.lit_bs.append('\\')
                p.lit_bs.append('\n')
                break
            r = p.rune()
        if l_start < 0:
            r = p.rune()
            continue
        # Compare the current line with the stop word.
        line = p.lit_bs[l_start:]
        if r != _EOF_RUNE and len(line) > 0:
            line = line[:-1]  # minus \n
        line_str = ''.join(line)
        if line_str == stop:
            p.hdoc_stops[-1] = None
            full = end_lit(p)
            val = full[:l_start]
            if val == '':
                return None
            return p.word_one(p.lit(pos, val))
        r = p.rune()


def advance_lit_re(p: 'parser.Parser', r: str) -> None:
    new_lit(p, r)
    while True:
        if r == '\\':
            p.rune()
        elif r == '(':
            p.rx_open_parens += 1
        elif r == ')':
            p.rx_open_parens -= 1
            if p.rx_open_parens < 0:
                p.tok, p.val = Token.LIT_WORD_, end_lit(p)
                p.quote = p._TEST_EXPR
                return
        elif r in (' ', '\t', '\r', '\n', ';', '&', '>', '<'):
            if p.rx_open_parens <= 0:
                p.tok, p.val = Token.LIT_WORD_, end_lit(p)
                p.quote = p._TEST_EXPR
                return
        elif r in ('"', '\'', '$', '`'):
            p.tok, p.val = Token.LIT_, end_lit(p)
            return
        elif r == _EOF_RUNE:
            p.tok, p.val = Token.LIT_WORD_, end_lit(p)
            p.quote = p._NO_STATE
            return
        r = p.rune()


##


def test_unary_op(val: str) -> UnTestOperator | None:
    if val == '!':
        return UnTestOperator.TS_NOT
    elif val == '-e' or val == '-a':
        return UnTestOperator.TS_EXISTS
    elif val == '-f':
        return UnTestOperator.TS_REG_FILE
    elif val == '-d':
        return UnTestOperator.TS_DIRECT
    elif val == '-c':
        return UnTestOperator.TS_CHAR_SP
    elif val == '-b':
        return UnTestOperator.TS_BLCK_SP
    elif val == '-p':
        return UnTestOperator.TS_NM_PIPE
    elif val == '-S':
        return UnTestOperator.TS_SOCKET
    elif val == '-L' or val == '-h':
        return UnTestOperator.TS_SMB_LINK
    elif val == '-k':
        return UnTestOperator.TS_STICKY
    elif val == '-g':
        return UnTestOperator.TS_GID_SET
    elif val == '-u':
        return UnTestOperator.TS_UID_SET
    elif val == '-G':
        return UnTestOperator.TS_GRP_OWN
    elif val == '-O':
        return UnTestOperator.TS_USR_OWN
    elif val == '-N':
        return UnTestOperator.TS_MODIF
    elif val == '-r':
        return UnTestOperator.TS_READ
    elif val == '-w':
        return UnTestOperator.TS_WRITE
    elif val == '-x':
        return UnTestOperator.TS_EXEC
    elif val == '-s':
        return UnTestOperator.TS_NO_EMPTY
    elif val == '-t':
        return UnTestOperator.TS_FD_TERM
    elif val == '-z':
        return UnTestOperator.TS_EMP_STR
    elif val == '-n':
        return UnTestOperator.TS_NEMP_STR
    elif val == '-o':
        return UnTestOperator.TS_OPT_SET
    elif val == '-v':
        return UnTestOperator.TS_VAR_SET
    elif val == '-R':
        return UnTestOperator.TS_REF_VAR
    else:
        return None


def test_binary_op(val: str) -> BinTestOperator | None:
    if val == '=':
        return BinTestOperator.TS_MATCH_SHORT
    elif val == '==':
        return BinTestOperator.TS_MATCH
    elif val == '!=':
        return BinTestOperator.TS_NO_MATCH
    elif val == '=~':
        return BinTestOperator.TS_RE_MATCH
    elif val == '-nt':
        return BinTestOperator.TS_NEWER
    elif val == '-ot':
        return BinTestOperator.TS_OLDER
    elif val == '-ef':
        return BinTestOperator.TS_DEV_INO
    elif val == '-eq':
        return BinTestOperator.TS_EQL
    elif val == '-ne':
        return BinTestOperator.TS_NEQ
    elif val == '-le':
        return BinTestOperator.TS_LEQ
    elif val == '-ge':
        return BinTestOperator.TS_GEQ
    elif val == '-lt':
        return BinTestOperator.TS_LSS
    elif val == '-gt':
        return BinTestOperator.TS_GTR
    else:
        return None
