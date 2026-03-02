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

from .tokens import UnTestOperator
from .tokens import BinTestOperator
from .tokens import Token
from .langs import lang_in
from .langs import LANG_ZSH


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
const escNewl rune = utf8.RuneSelf + 1


def parser_rune(p: Parser) -> str:
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
def parser_fill(p: Parser, n: int) -> None:
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

func (p *Parser) nextKeepSpaces() {
    r := p.r
    if p.quote != hdocBody and p.quote != hdocBodyTabs {
        # Heredocs handle escaped newlines in a special way, but others do not.
        for r == escNewl {
            r = p.rune()

    p.pos = p.nextPos()
    switch p.quote {
    case runeByRune:
        p.tok = illegalTok
    case dblQuotes:
        switch r {
        case '`', '"', '$':
            p.tok = p.dqToken(r)
        default:
            p.advanceLitDquote(r)
    case hdocBody, hdocBodyTabs:
        switch r {
        case '`', '$':
            p.tok = p.dqToken(r)
        default:
            p.advanceLitHdoc(r)
    case paramExpRepl:
        if r == '/' {
            p.rune()
            p.tok = slash
            break
        fallthrough
    case paramExpExp:
        switch r {
        case '}':
            p.tok = p.param_token(r)
        case '`', '"', '$', '\'':
            p.tok = p.reg_token(r)
        default:
            p.advanceLitOther(r)

    if p.err is not None:
        p.tok = Token.EOF_

func (p *Parser) next():
    if p.r == utf8.RuneSelf:
        p.tok = Token.EOF_
        return

    p.spaced = False
    if p.quote&allKeepSpaces != 0:
        p.nextKeepSpaces()
        return

    r := p.r
    for r == escNewl:
        r = p.rune()

skipSpace:
    for:
        switch r:
        case utf8.RuneSelf:
            p.tok = Token.EOF_
            return
        case escNewl:
            r = p.rune()
        case ' ', '\t', '\r':
            p.spaced = True
            r = p.rune()
        case '\n':
            if p.tok == Token.NEWL_:
                # merge consecutive newline tokens
                r = p.rune()
                continue

            p.spaced = True
            p.tok = Token.NEWL_
            if p.quote != hdocWord and len(p.heredocs) > p.buriedHdocs {
                p.doHeredocs()

            return
        default:
            break skipSpace

    if p.stopAt is not None and (p.spaced or p.tok == illegalTok or p.stopToken()) {
        w := utf8.RuneLen(r)
        if bytes.HasPrefix(p.bs[p.bsp-uint(w):], p.stopAt) {
            p.r = utf8.RuneSelf
            p.w = 1
            p.tok = Token.EOF_
            return

    p.pos = p.nextPos()
    switch {
    case p.quote&allRegTokens != 0:
        switch r {
        case ';', '"', '\'', '(', ')', '$', '|', '&', '>', '<', '`':
            if r == '<' and lang_in(p.lang, LANG_ZSH) and p.zshNumRange() {
                p.advance_lit_none(r)
                return
            p.tok = p.reg_token(r)
        case '#':
            # If we're parsing $foo#bar, ${foo}#bar, 'foo'#bar, or "foo"#bar,
            # #bar is a continuation of the same word, not a comment.
            if p.quote == unquotedWordCont and not p.spaced {
                p.advance_lit_none(r)
                return
            r = p.rune()
            p.new_lit(r)
        runeLoop:
            for {
                switch r {
                case '\n', utf8.RuneSelf:
                    break runeLoop
                case escNewl:
                    p.litBs = append(p.litBs, '\\', '\n')
                    break runeLoop
                case '`':
                    if p.backquoteEnd() {
                        break runeLoop
                r = p.rune()
            if p.keepComments {
                *p.curComs = append(*p.curComs, Comment{
                    Hash: p.pos,
                    Text: p.end_lit(),
            else {
                p.litBs = nil
            p.next()
        case '[':
            if p.quote == arrayElems {
                p.rune()
                p.tok = Token.LEFT_BRACK
            else {
                p.advance_lit_none(r)
        case '=':
            if p.peek() == '(' {
                p.rune()
                p.rune()
                p.tok = Token.ASSGN_PAREN
            else if p.quote == arrayElems {
                p.rune()
                p.tok = Token.ASSGN
            else {
                p.advance_lit_none(r)
        case '?', '*', '+', '@', '!':
            if p.extended_glob() {
                switch r {
                case '?':
                    p.tok = Token.GLOB_QUEST
                case '*':
                    p.tok = Token.GLOB_STAR
                case '+':
                    p.tok = Token.GLOB_PLUS
                case '@':
                    p.tok = Token.GLOB_AT
                case '!':
                    p.tok = Token.GLOB_EXCL
                p.rune()
                p.rune()
            else {
                p.advance_lit_none(r)
        default:
            p.advance_lit_none(r)
    case p.quote&allArithmExpr != 0 and arithm_ops(r):
        p.tok = p.arithm_token(r)
    case p.quote&allParamExp != 0 and param_ops(r):
        p.tok = p.param_token(r)
    case p.quote == testExprRegexp:
        if not p.rxFirstPart and p.spaced {
            p.quote = testExpr
            goto skipSpace
        p.rxFirstPart = False
        switch r {
        case ';', '"', '\'', '$', '&', '>', '<', '`':
            p.tok = p.reg_token(r)
        case ')':
            if p.rxOpenParens > 0 {
                # continuation of open paren
                p.advanceLitRe(r)
            else {
                p.tok = rightParen
                p.quote = testExpr
                p.rune() # we are tokenizing manually
        default: # including '(', '|'
            p.advanceLitRe(r)
    case reg_ops(r):
        p.tok = p.reg_token(r)
    default:
        p.advanceLitOther(r)
    if p.err is not None:
        p.tok = Token.EOF_

# extended_glob determines whether we're parsing a Bash extended globbing expression.
# For example, whether `*` or `@` are followed by `(` to form `@(foo)`.
def extended_glob(p: Parser) -> bool:
    if lang_in(p.lang, LANG_ZSH) {
        # Zsh doesn't have extended globs like bash/mksh.
        # We still tokenize +( @( !( so the parser can give a clear error,
        # but not *( or ?( as those are used in zsh glob qualifiers.
        switch p.r {
        case '+', '@', '!':
        default:
            return False
    if p.val == "function" {
        # We don't support e.g. `function @() { ... }` at the moment, but we could.
        return False
    if p.peek() == '(' {
        # NOTE: empty pattern list is a valid globbing syntax like `@()`,
        # but we'll operate on the "likelihood" that it is a function;
        # only tokenize if its a non-empty pattern list.
        # We do this after peeking for just one byte, so that the input `echo *`
        # followed by a newline does not hang an interactive shell parser until
        # another byte is input.
        _, p2 := p.peekTwo()
        return p2 != ')'
    return False

func (p *Parser) peek() byte {
    if int(p.bsp) >= len(p.bs) {
        p.fill()
    if int(p.bsp) >= len(p.bs) {
        return utf8.RuneSelf
    return p.bs[p.bsp]

func (p *Parser) peekTwo() (byte, byte) {
    # TODO: This should loop for slow readers, e.g. those providing one byte at
    # a time. Use a loop and test it with [testing/iotest.OneByteReader].
    if int(p.bsp+1) >= len(p.bs) {
        p.fill()
    if int(p.bsp) >= len(p.bs) {
        return utf8.RuneSelf, utf8.RuneSelf
    if int(p.bsp+1) >= len(p.bs) {
        return p.bs[p.bsp], utf8.RuneSelf
    return p.bs[p.bsp], p.bs[p.bsp+1]

def reg_token(p: Parser, r: str) -> Token:
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
        if p.rune() == '(' and lang_in(p.lang, LANG_BASH_LIKE|LANG_MIR_BSD_KORN|LANG_ZSH) and p.quote != testExpr:
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
            r = p.rune()
            if r == '-':
                p.rune()
                return Token.DASH_HDOC
            elif r == '<':
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

func (p *Parser) dqToken(r rune) token {
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
                break
            p.rune()
            return Token.DOLL_BRACK
        elif pr == '(':
            if p.rune() == '(':
                p.rune()
                return Token.DOLL_DBL_PAREN
            return Token.DOLL_PAREN
        return Token.DOLLAR
    raise RuntimeError('unreachable')

def param_token(p: Parser, r: str) -> Token:
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
            return Token.COL_ASSIGN
        elif pr == '#':
            p.rune()
            return Token.COL_HASH
        return colon
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
        return perc
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

    # This func gets called by the parser in [runeByRune] mode;
    # we need to handle EOF and unexpected runes.
    case utf8.RuneSelf:
        return Token.EOF_
    else:
        return Tokkens.ILLEGAL_TOK_
"""  # noqa

def arithm_token(p: Parser, r: str) -> Token:
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


r"""
def new_lit(p: Parser, r: str) -> None:
    if r < utf8.RuneSelf:
        p.litBs = p.litBuf[:1]
        p.litBs[0] = byte(r)
    case r > escNewl:
        w := utf8.RuneLen(r)
        p.litBs = append(p.litBuf[:0], p.bs[p.bsp-uint(w):p.bsp]...)
    default:
        # don't let r == utf8.RuneSelf go to the second case as [utf8.RuneLen]
        # would return -1
        p.litBs = p.litBuf[:0]

func (p *Parser) end_lit() (s string) {
    if p.r == utf8.RuneSelf or p.r == escNewl {
        s = string(p.litBs)
    else {
        s = string(p.litBs[:len(p.litBs)-p.w])
    p.litBs = nil
    return s

func (p *Parser) isLitRedir() bool {
    lit := p.litBs[:len(p.litBs)-1]
    if lit[0] == '{' and lit[len(lit)-1] == '}' {
        return ValidName(string(lit[1 : len(lit)-1]))
    return numberLiteral(lit)

def single_rune_param(r: str) -> bool:
    if r in ('@', '*', '#', '$', '?', '!', '-', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9'):
        return True
    return False

func param_name_rune[T rune | byte](r T) bool {
    return ascii_letter(r) or ascii_digit(r) or r == '_'

func (p *Parser) advanceLitOther(r rune) {
    tok := Token.LIT_WORD_
loop:
    for p.new_lit(r); r != utf8.RuneSelf; r = p.rune() {
        switch r {
        case '\\': # escaped byte follows
            p.rune()
        case '\'', '"', '`', '$':
            tok = Token.LIT_
            break loop
        case '}':
            if p.quote&allParamExp != 0 {
                break loop
        case '/':
            if p.quote != paramExpExp {
                break loop
        case ':', '=', '%', '^', ',', '?', '!', '~', '*':
            if p.quote&allArithmExpr != 0 {
                break loop
        case '.':
            if not lang_in(p.lang, LANG_ZSH) and p.quote&allArithmExpr != 0 {
                break loop
        case '[', ']':
            if lang_in(p.lang, LANG_BASH_LIKE|LANG_MIR_BSD_KORN|LANG_ZSH) and p.quote&allArithmExpr != 0 {
                break loop
            fallthrough
        case '+', '-', ' ', '\t', ';', '&', '>', '<', '|', '(', ')', '\n', '\r':
            if p.quote&allKeepSpaces == 0 {
                break loop
    p.tok, p.val = tok, p.end_lit()

# litBsGlob reports whether the literal bytes accumulated so far
# contain a glob metacharacter, excluding the last byte which is '('.
func (p *Parser) litBsGlob() bool {
    # Exclude the last byte which is the '(' that triggered this check.
    for _, b := range p.litBs[:len(p.litBs)-1] {
        switch b {
        case '*', '?', '[':
            return True
        case '/':
            # Paths like /bin/sh(:t) can also have glob qualifiers;
            # function names never contain slashes.
            return True
    return False

# zshNumRange peeks at the bytes after '<' to check for a zsh numeric
# range glob pattern like <->, <5->, <-10>, or <5-10>.
func (p *Parser) zshNumRange() bool {
    # Peeking a handful of bytes here should be enough.
    # TODO: This should loop for slow readers, e.g. those providing one byte at
    # a time. Use a loop and test it with [testing/iotest.OneByteReader].
    if int(p.bsp) >= len(p.bs) {
        p.fill()
    rest := p.bs[p.bsp:]
    for len(rest) > 0 and rest[0] >= '0' and rest[0] <= '9' {
        rest = rest[1:]
    if len(rest) == 0 or rest[0] != '-' {
        return False
    rest = rest[1:]
    for len(rest) > 0 and rest[0] >= '0' and rest[0] <= '9' {
        rest = rest[1:]
    return len(rest) > 0 and rest[0] == '>'

func (p *Parser) advance_lit_none(r rune) {
    p.eql_offs = -1
    tok = Token.LIT_WORD_
loop:
    for p.new_lit(r); r != utf8.RuneSelf; r = p.rune():
        if r in (' ', '\t', '\n', '\r', '&', '|', ';', ')'):
            break loop
        elif r == '(':
            if lang_in(p.lang, LANG_ZSH) and p.litBsGlob():
                # Zsh glob qualifiers like *(.), **(/) or *(om[1,5]); consume until ')'.
                for {
                    if r = p.rune(); r == utf8.RuneSelf or r == ')':
                        break
                continue
            break loop
        elif r == '\\': # escaped byte follows
            p.rune()
        elif r in ('>', '<'):
            if r == '<' and lang_in(p.lang, LANG_ZSH) and p.zshNumRange():
                # Zsh numeric range glob like <-> or <1-100>; consume until '>'.
                for {
                    if r = p.rune(); r == '>' or r == utf8.RuneSelf:
                        break
                continue
            if p.peek() == '(' {
                tok = Token.LIT_
            else if p.isLitRedir() {
                tok = Token.LIT_REDIR_
            break loop
        elif r == '`':
            if p.quote != subCmdBckquo {
                tok = Token.LIT_
            break loop
        elif r in ('"', '\'', '$'):
            tok = Token.LIT_
            break loop
        elif r in ('?', '*', '+', '@', '!'):
            if p.extended_glob():
                tok = Token.LIT_
                break loop
        elif r == '=':
            if p.eqlOffs < 0 {
                p.eqlOffs = len(p.litBs) - 1
        elif r == '[':
            if lang_in(p.lang, LANG_BASH_LIKE|LANG_MIR_BSD_KORN|LANG_ZSH) and len(p.litBs) > 1 and p.litBs[0] != '[' {
                tok = Token.LIT_
                break loop
    p.tok, p.val = tok, p.end_lit()

func (p *Parser) advanceLitDquote(r rune) {
    tok := Token.LIT_WORD_
loop:
    for p.new_lit(r); r != utf8.RuneSelf; r = p.rune() {
        switch r {
        case '"':
            break loop
        case '\\': # escaped byte follows
            p.rune()
        case escNewl, '`', '$':
            tok = _Lit
            break loop
    p.tok, p.val = tok, p.end_lit()

func (p *Parser) advanceLitHdoc(r rune) {
    # Unlike the rest of nextKeepSpaces quote states, we handle escaped
    # newlines here. If lastTok==_Lit, then we know we're following an
    # escaped newline, so the first line can't end the heredoc.
    lastTok := p.tok
    for r == escNewl {
        r = p.rune()
        lastTok = _Lit
    p.pos = p.nextPos()

    p.tok = _Lit
    p.new_lit(r)
    for p.quote == hdocBodyTabs and r == '\t' {
        r = p.rune()
    lStart := len(p.litBs) - 1
    stop := p.hdocStops[len(p.hdocStops)-1]
    for ; ; r = p.rune() {
        switch r {
        case escNewl, '$':
            p.val = p.end_lit()
            return
        case '\\': # escaped byte follows
            p.rune()
        case '`':
            if not p.backquoteEnd() {
                p.val = p.end_lit()
                return
            fallthrough
        case '\n', utf8.RuneSelf:
            if p.parsingDoc {
                if r == utf8.RuneSelf {
                    p.tok = Token.LIT_WORD_
                    p.val = p.end_lit()
                    return
            else if lStart == 0 and lastTok == _Lit {
                # This line starts right after an escaped
                # newline, so it should never end the heredoc.
            else if lStart >= 0 {
                # Compare the current line with the stop word.
                line := p.litBs[lStart:]
                if r != utf8.RuneSelf and len(line) > 0 {
                    line = line[:len(line)-1] # minus trailing character
                if bytes.Equal(line, stop) {
                    p.tok = Token.LIT_WORD_
                    p.val = p.end_lit()[:lStart]
                    if p.val == "" {
                        p.tok = Token.NEWL_
                    p.hdocStops[len(p.hdocStops)-1] = nil
                    return
            if r != '\n' {
                return # hit an unexpected EOF or closing backquote
            for p.quote == hdocBodyTabs and p.peek() == '\t' {
                p.rune()
            lStart = len(p.litBs)

func (p *Parser) quotedHdocWord() *Word {
    r := p.r
    p.new_lit(r)
    pos := p.nextPos()
    stop := p.hdocStops[len(p.hdocStops)-1]
    for ; ; r = p.rune() {
        if r == utf8.RuneSelf {
            return nil
        for p.quote == hdocBodyTabs and r == '\t' {
            r = p.rune()
        lStart := len(p.litBs) - 1
    runeLoop:
        for {
            switch r {
            case utf8.RuneSelf, '\n':
                break runeLoop
            case '`':
                if p.backquoteEnd() {
                    break runeLoop
            case escNewl:
                p.litBs = append(p.litBs, '\\', '\n')
                break runeLoop
            r = p.rune()
        if lStart < 0 {
            continue
        # Compare the current line with the stop word.
        line := p.litBs[lStart:]
        if r != utf8.RuneSelf and len(line) > 0 {
            line = line[:len(line)-1] # minus \n
        if bytes.Equal(line, stop) {
            p.hdocStops[len(p.hdocStops)-1] = nil
            val := p.end_lit()[:lStart]
            if val == "" {
                return nil
            return p.wordOne(p.lit(pos, val))

func (p *Parser) advanceLitRe(r rune) {
    for p.new_lit(r); ; r = p.rune() {
        switch r {
        case '\\':
            p.rune()
        case '(':
            p.rxOpenParens++
        case ')':
            if p.rxOpenParens--; p.rxOpenParens < 0 {
                p.tok, p.val = Token.LIT_WORD_, p.end_lit()
                p.quote = testExpr
                return
        case ' ', '\t', '\r', '\n', ';', '&', '>', '<':
            if p.rxOpenParens <= 0 {
                p.tok, p.val = Token.LIT_WORD_, p.end_lit()
                p.quote = testExpr
                return
        case '"', '\'', '$', '`':
            p.tok, p.val = _Lit, p.end_lit()
            return
        case utf8.RuneSelf:
            p.tok, p.val = Token.LIT_WORD_, p.end_lit()
            p.quote = noState
            return
"""  # noqa


def test_unary_op(val: str) -> UnTestOperator | None:
    if val == "!":
        return UnTestOperator.TS_NOT
    elif val == "-e" or val == "-a":
        return UnTestOperator.TS_EXISTS
    elif val == "-f":
        return UnTestOperator.TS_REG_FILE
    elif val == "-d":
        return UnTestOperator.TS_DIRECT
    elif val == "-c":
        return UnTestOperator.TS_CHAR_SP
    elif val == "-b":
        return UnTestOperator.TS_BLCK_SP
    elif val == "-p":
        return UnTestOperator.TS_NM_PIPE
    elif val == "-S":
        return UnTestOperator.TS_SOCKET
    elif val == "-L" or val == "-h":
        return UnTestOperator.TS_SMB_LINK
    elif val == "-k":
        return UnTestOperator.TS_STICKY
    elif val == "-g":
        return UnTestOperator.TS_GID_SET
    elif val == "-u":
        return UnTestOperator.TS_UID_SET
    elif val == "-G":
        return UnTestOperator.TS_GRP_OWN
    elif val == "-O":
        return UnTestOperator.TS_USR_OWN
    elif val == "-N":
        return UnTestOperator.TS_MODIF
    elif val == "-r":
        return UnTestOperator.TS_READ
    elif val == "-w":
        return UnTestOperator.TS_WRITE
    elif val == "-x":
        return UnTestOperator.TS_EXEC
    elif val == "-s":
        return UnTestOperator.TS_NO_EMPTY
    elif val == "-t":
        return UnTestOperator.TS_FD_TERM
    elif val == "-z":
        return UnTestOperator.TS_EMP_STR
    elif val == "-n":
        return UnTestOperator.TS_NEMP_STR
    elif val == "-o":
        return UnTestOperator.TS_OPT_SET
    elif val == "-v":
        return UnTestOperator.TS_VAR_SET
    elif val == "-R":
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
