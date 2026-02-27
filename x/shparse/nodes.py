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
import abc
import io
import typing as ta

from omlish import dataclasses as dc
from omlish import lang

from .tokens import RedirOperator
from .tokens import ProcOperator
from .tokens import GlobOperator
from .tokens import BinCmdOperator
from .tokens import UnTestOperator
from .tokens import BinTestOperator


##


# Node represents a syntax tree node.
@dc.dataclass()
class Node(lang.Abstract):
    # Pos returns the position of the first character of the node. Comments
    # are ignored, except if the node is a [*File].
    def pos(self) -> 'Pos':
        raise NotImplementedError

    # End returns the position of the character immediately after the node.
    # If the character is a newline, the line number won't cross into the
    # next line. Comments are ignored, except if the node is a [*File].
    def end(self) -> 'Pos':
        raise NotImplementedError


# File represents a shell source file.
@dc.dataclass()
class File(Node):
    name: str

    stmts: list['Stmt']
    last: list['Comment']

    def pos(self) -> 'Pos':
        return stmts_pos(self.stmts, self.last)
    
    def end(self) -> 'Pos':
        return stmts_end(self.stmts, self.last)


def stmts_pos(stmts: list['Stmt'], last: list['Comment']) -> 'Pos':
    if len(stmts) > 0:
        s = stmts[0]
        s_pos = s.pos()
        if len(s.comments) > 0:
            c_pos = s.comments[0].pos()
            if s_pos.after(c_pos):
                return c_pos
        return s_pos
    if len(last) > 0:
        return last[0].pos()
    return Pos()


def stmts_end(stmts: list['Stmt'], last: list['Comment']) -> 'Pos':
    if len(last) > 0:
        return last[len(last)-1].end()
    if len(stmts) > 0:
        s = stmts[len(stmts)-1]
        s_end = s.end()
        if len(s.comments) > 0:
            c_end = s.comments[0].end()
            if c_end.after(s_end):
                return c_end
        return s_end
    return Pos()


# Pos is a position within a shell source file.
@dc.dataclass()
class Pos:
    offs: int = 0
    line_col: int = 0

    # Offset returns the byte offset of the position in the original source file.
    # Byte offsets start at 0. Invalid positions always report the offset 0.
    #
    # Offset has basic protection against overflows; if an input is too large,
    # offset numbers will stop increasing past a very large number.
    def offset(self) -> int:
        if self.offs > OFFSET_MAX:
            return 0 # invalid
        return self.offs

    # Line returns the line number of the position, starting at 1.
    # Invalid positions always report the line number 0.
    #
    # Line is protected against overflows; if an input has too many lines, extra
    # lines will have a line number of 0, rendered as "?" by [Pos.String].
    def line(self) -> int:
        return self.line_col >> COL_BIT_SIZE

    # Col returns the column number of the position, starting at 1. It counts in
    # bytes. Invalid positions always report the column number 0.
    #
    # Col is protected against overflows; if an input line has too many columns,
    # extra columns will have a column number of 0, rendered as "?" by [Pos.String].
    def col(self) -> int:
        return self.line_col & COL_BIT_MASK

    def string(self) -> str:
        b = io.StringIO()
        line = self.line()
        if line > 0:
            b.write(str(line))
        else:
            b.write('?')
        b.write(':')
        col = self.col()
        if col > 0:
            b.write(str(col))
        else:
            b.write('?')
        return b.getvalue()

    # IsValid reports whether the position contains useful position information.
    # Some positions returned via [Parse] may be invalid: for example, [Stmt.Semicolon]
    # will only be valid if a statement contained a closing token such as ';'.
    #
    # Recovered positions, as reported by [Pos.IsRecovered], are not considered valid
    # given that they don't contain position information.
    def is_valid(self) -> bool:
        return self.offs <= OFFSET_MAX and self.line_col != 0

    # IsRecovered reports whether the position that the token or node belongs to
    # was missing in the original input and recovered via [RecoverErrors].
    def is_recovered(self) -> bool:
        return self == RECOVERED_POS

    # After reports whether the position p is after p2. It is a more expressive
    # version of p.Offset() > p2.Offset().
    # It always returns false if p is an invalid position.
    def after(self, p2: 'Pos') -> bool:
        if not self.is_valid():
            return False
        return self.offs > p2.offs


# Offsets use 32 bits for a reasonable amount of precision.
# We reserve a few of the highest values to represent types of invalid positions.
# We leave some space before the real uint32 maximum so that we can easily detect
# when arithmetic on invalid positions is done by mistake.
OFFSET_RECOVERED = (1<<32 - 1) - 10
OFFSET_MAX       = (1<<32 - 1) - 11

# We used to split line and column numbers evenly in 16 bits, but line numbers
# are significantly more important in practice. Use more bits for them.

LINE_BIT_SIZE = 18
LINE_MAX      = (1 << LINE_BIT_SIZE) - 1

COL_BIT_SIZE = 32 - LINE_BIT_SIZE
COL_MAX      = (1 << COL_BIT_SIZE) - 1
COL_BIT_MASK = COL_MAX


RECOVERED_POS = Pos(offs=OFFSET_RECOVERED)


# TODO(v4): consider using uint32 for Offset/Line/Col to better represent bit sizes.
# Or go with int64, which more closely resembles portable "sizes" elsewhere.
# The latter is probably nicest, as then we can change the number of internal
# bits later, and we can also do overflow checks for the user in NewPos.

# NewPos creates a position with the given offset, line, and column.
#
# Note that [Pos] uses a limited number of bits to store these numbers.
# If line or column overflow their allocated space, they are replaced with 0.
def new_pos(offset: int, line: int, column: int) -> Pos:
    # Basic protection against offset overflow;
    # note that an offset of 0 is valid, so we leave the maximum.
    offset = min(offset, OFFSET_MAX)
    if line > LINE_MAX:
        line = 0  # protect against overflows; rendered as "?"
    if column > COL_MAX:
        column = 0  # protect against overflows; rendered as "?"
    return Pos(
        offs=offset,
        line_col=(line << COL_BIT_SIZE) | column,
    )


def pos_add_col(p: Pos, n: int) -> Pos:
    if not p.is_valid():
        return p
    # TODO: guard against overflows
    p.line_col += n
    p.offs += n
    return p


def pos_max(p1: Pos, p2: Pos) -> Pos:
    if p2.after(p1):
        return p2
    return p1


# Comment represents a single comment on a single line.
@dc.dataclass()
class Comment(Node):
    hash: Pos
    text: str

    def pos(self) -> Pos:
        return self.hash

    def end(self) -> Pos:
        return pos_add_col(self.hash, 1 + len(self.text))


# Stmt represents a statement, also known as a "complete command". It is
# compromised of a command and other components that may come before or after
# it.
@dc.dataclass()
class Stmt(Node):
    comments: list['Comment']
    cmd: ta.Optional['Command']

    position: Pos
    semicolon: Pos  # position of ';', '&', or '|&', if any

    negated: bool    # ! stmt
    background: bool # stmt &
    coprocess: bool  # mksh's |&

    redirs: list['Redirect']  # stmt >a <b

    def pos(self) -> Pos:
        return self.position
    
    def end(self) -> Pos:
        if self.semicolon.is_valid():
            end = pos_add_col(self.semicolon, 1)  # ';' or '&'
            if self.coprocess:
                end = pos_add_col(end, 1)  # '|&'
            return end
        end = self.position
        if self.negated:
            end = pos_add_col(end, 1)
        if self.cmd is not None:
            end = self.cmd.end()
        if self.redirs:
            end = pos_max(end, self.redirs[-1].end())
        return end


# Command represents all nodes that are simple or compound commands, including
# function declarations.
#
# These are:
# - [*CallExpr]
# - [*IfClause]
# - [*WhileClause]
# - [*ForClause]
# - [*CaseClause]
# - [*Block]
# - [*Subshell]
# - [*BinaryCmd]
# - [*FuncDecl]
# - [*ArithmCmd]
# - [*TestClause],
# - [*DeclClause]
# - [*LetClause]
# - [*TimeClause]
# - [*CoprocClause].
@dc.dataclass()
class Command(Node, lang.Abstract):
    pass


# Assign represents an assignment to a variable.
#
# Here and elsewhere, Index can mean either an index expression into an indexed
# array, or a string key into an associative array.
#
# If Index is non-nil, the value will be a word and not an array as nested
# arrays are not allowed.
#
# If Naked is true and Name is nil, the assignment is part of a [DeclClause] and
# the argument (in the Value field) will be evaluated at run-time. This
# includes parameter expansions, which may expand to assignments or options.
@dc.dataclass()
class Assign(Node):
    append: bool                      # +=
    naked: bool                       # without '='

    name: ta.Optional['Lit']         = None  # must be a valid name
    index: ta.Optional['ArithmExpr'] = None  # [i], ["k"]
    value: ta.Optional['Word']       = None  # =val
    array: ta.Optional['ArrayExpr']  = None  # =(arr)

    def pos(self) -> Pos:
        if not self.name is None:
            return self.value.pos()
        return self.name.pos()

    def end(self) -> Pos:
        if self.value is not None:
            return self.value.end()
        if self.array is not None:
            return self.array.end()
        if self.index is not None:
            return pos_add_col(self.index.end(), 2)
        if self.naked:
            return self.name.end()
        return pos_add_col(self.name.end(), 1)


# Redirect represents an input/output redirection.
@dc.dataclass()
class Redirect(Node):
    op_pos: Pos
    op: RedirOperator
    n: ta.Optional['Lit'] = None      # fd>, or {varname}> in Bash
    word: ta.Optional['Word'] = None  # >word
    hdoc: ta.Optional['Word'] = None  # here-document body

    def pos(self) -> Pos:
        if self.n is not None:
            return self.n.pos()
        return self.op_pos

    def end(self) -> Pos:
        if self.hdoc is not None:
            return self.hdoc.end()
        return self.word.end()


# CallExpr represents a command execution or function call, otherwise known as
# a "simple command".
#
# If Args is empty, Assigns apply to the shell environment. Otherwise, they are
# variables that cannot be arrays and which only apply to the call.
@dc.dataclass()
class CallExpr(Command):
    assigns: list[Assign]  # a=x b=y args
    args: list['Word']

    def pos(self) -> Pos:
        if self.assigns:
            return self.assigns[0].pos()
        return self.args[0].pos()

    def end(self) -> Pos:
        if len(self.args) == 0:
            return self.assigns[-1].end()
        return self.args[-1].end()


# Subshell represents a series of commands that should be executed in a nested
# shell environment.
@dc.dataclass()
class Subshell(Command):
    lparen: Pos
    rparen: Pos

    stmts: list['Stmt']
    last: list['Comment']

    def pos(self) -> Pos:
        return self.lparen
    
    def end(self) -> Pos:
        return pos_add_col(self.rparen, 1)


# Block represents a series of commands that should be executed in a nested
# scope. It is essentially a list of statements within curly braces.
@dc.dataclass()
class Block(Command):
    lbrace: Pos
    rbrace: Pos

    stmts: list['Stmt']
    last: list['Comment']

    def pos(self) -> Pos:
        return self.lbrace
    
    def end(self) -> Pos:
        return pos_add_col(self.rbrace, 1)


# IfClause represents an if statement.
@dc.dataclass()
class IfClause(Command):
    position: Pos  # position of the starting "if", "elif", or "else" token
    then_pos: Pos  # position of "then", empty if this is an "else"
    fi_pos: Pos    # position of "fi", shared with .Else if non-nil

    cond: list['Stmt']
    cond_last: list['Comment']
    then: list['Stmt']
    then_last: list['Comment']

    else_: ta.Optional['IfClause']  # if non-nil, an "elif" or an "else"

    last: list['Comment']  # comments on the first "elif", "else", or "fi"

    def pos(self) -> Pos:
        return self.position
    
    def end(self) -> Pos:
        return pos_add_col(self.fi_pos, 2)


# WhileClause represents a while or an until clause.
@dc.dataclass()
class WhileClause(Command):
    while_pos: Pos
    do_pos: Pos
    done_pos: Pos
    until: bool

    cond: list['Stmt']
    cond_last: list['Comment']
    do: list['Stmt']
    do_last: list['Comment']

    def pos(self) -> Pos:
        return self.while_pos
    
    def end(self) -> Pos:
        return pos_add_col(self.done_pos, 4)


# ForClause represents a for or a select clause. The latter is only present in
# Bash.
@dc.dataclass()
class ForClause(Command):
    for_pos: Pos
    do_pos: Pos
    done_pos: Pos
    select: bool
    braces: bool  # deprecated form with { } instead of do/done
    loop: 'Loop'

    do: list['Stmt']
    do_last: list['Comment']

    def pos(self) -> Pos:
        return self.for_pos
    
    def end(self) -> Pos:
        return pos_add_col(self.done_pos, 4)


# Loop holds either [*WordIter] or [*CStyleLoop].
@dc.dataclass()
class Loop(Node, lang.Abstract):
    pass


# WordIter represents the iteration of a variable over a series of words in a
# for clause. If InPos is an invalid position, the "in" token was missing, so
# the iteration is over the shell's positional parameters.
@dc.dataclass()
class WordIter(Loop):
    name: 'Lit'
    in_pos: Pos  # position of "in"
    items: list['Word']

    def pos(self) -> Pos:
        return self.name.pos()
    
    def end(self) -> Pos:
        if len(self.items) > 0:
            return word_last_end(self.items)
        return pos_max(self.name.end(), pos_add_col(self.in_pos, 2))


# CStyleLoop represents the behavior of a for clause similar to the C
# language.
#
# This node will only appear with [LANG_BASH].
@dc.dataclass()
class CStyleLoop(Loop):
    lparen: Pos
    rparen: Pos

    # Init, Cond, Post can each be nil, if the for loop construct omits it.
    init: ta.Optional['ArithmExpr'] = None
    cond: ta.Optional['ArithmExpr'] = None
    post: ta.Optional['ArithmExpr'] = None

    def pos(self) -> Pos:
        return self.lparen
    
    def end(self) -> Pos:
        return pos_add_col(self.rparen, 2)


# BinaryCmd represents a binary expression between two statements.
@dc.dataclass()
class BinaryCmd(Command):
    op_pos: Pos
    op: BinCmdOperator
    x: 'Stmt'
    y: 'Stmt'

    def pos(self) -> Pos:
        return self.x.pos()
    
    def end(self) -> Pos:
        return self.y.end()


# FuncDecl represents the declaration of a function.
@dc.dataclass()
class FuncDecl(Command):
    position: Pos
    rsrv_word: bool  # non-posix "function f" style
    parens: bool     # with () parentheses, can only be false when RsrvWord==true

    # Only one of these is set at a time.
    # Neither is set when declaring an anonymous func with [LANG_ZSH].
    # TODO(v4): join these, even if it's mildly annoying to non-Zsh users.
    name: 'Lit'
    names: list['Lit']  # When declaring many func names with [LANG_ZSH].

    body: Stmt

    def pos(self) -> Pos:
        return self.position
    
    def end(self) -> Pos:
        return self.body.end()


# ArithmExpr represents all nodes that form arithmetic expressions.
#
# These are:
# - [*BinaryArithm]
# - [*UnaryArithm]
# - [*ParenArithm]
# - [*FlagsArithm]
# - [*Word].
@dc.dataclass()
class ArithmExpr(Node, lang.Abstract):
    pass


# TestExpr represents all nodes that form test expressions.
#
# These are:
# - [*BinaryTest]
# - [*UnaryTest]
# - [*ParenTest]
# - [*Word].
@dc.dataclass()
class TestExpr(Node, lang.Abstract):
    pass


# Word represents a shell word, containing one or more word parts contiguous to
# each other. The word is delimited by word boundaries, such as spaces,
# newlines, semicolons, or parentheses.
@dc.dataclass()
class Word(ArithmExpr, TestExpr):
    parts: list['WordPart']

    def pos(self) -> Pos:
        return self.parts[0].pos()

    def end(self) -> Pos:
        return self.parts[-1].end()

    # Lit returns the word as a string when it is a simple literal,
    # made up of [*Lit] word parts only.
    # An empty string is returned otherwise.
    #
    # For example, the word "foo" will return "foo",
    # but the word "foo${bar}" will return "".
    def lit(self) -> str:
        # In the usual case, we'll have either a single part that's a literal,
        # or one of the parts being a non-literal. Using strings.Join instead
        # of a strings.Builder avoids extra work in these cases, since a single
        # part is a shortcut, and many parts don't incur string copies.
        lits: list[str] = []
        for part in self.parts:
            if not isinstance(part, Lit):
                return ""
            lits.append(part.value)
        return ''.join(lits)


# WordPart represents all nodes that can form part of a word.
#
# These are:
# - [*Lit]
# - [*SglQuoted]
# - [*DblQuoted]
# - [*ParamExp]
# - [*CmdSubst]
# - [*ArithmExp]
# - [*ProcSubst]
# - [*ExtGlob].
@dc.dataclass()
class WordPart(Node, lang.Abstract):
    pass


# Lit represents a string literal.
#
# Note that a parsed string literal may not appear as-is in the original source
# code, as it is possible to split literals by escaping newlines. The splitting
# is lost, but the end position is not.
@dc.dataclass()
class Lit(WordPart):
    value_pos: Pos
    value_end: Pos
    value: str

    def pos(self) -> Pos:
        return self.value_pos
    
    def end(self) -> Pos:
        return self.value_end


# SglQuoted represents a string within single quotes.
@dc.dataclass()
class SglQuoted(WordPart):
    left: Pos
    right: Pos
    dollar: bool  # $''
    value: str

    def pos(self) -> Pos:
        return self.left
    
    def end(self) -> Pos:
        return pos_add_col(self.right, 1)


# DblQuoted represents a list of nodes within double quotes.
@dc.dataclass()
class DblQuoted(WordPart):
    left: Pos
    right: Pos
    dollar: bool  # $""
    parts: list[WordPart]

    def pos(self) -> Pos:
        return self.left
    
    def end(self) -> Pos:
        return pos_add_col(self.right, 1)


# CmdSubst represents a command substitution.
@dc.dataclass()
class CmdSubst(WordPart):
    left: Pos
    right: Pos

    stmts: list['Stmt']
    last: list['Comment']

    backquotes: bool  # deprecated `foo`
    temp_file: bool   # mksh's ${ foo;}
    reply_var: bool   # mksh's ${|foo;}

    def pos(self) -> Pos:
        return self.left
    
    def end(self) -> Pos:
        return pos_add_col(self.right, 1)


r"""
# ParamExp represents a parameter expansion.
@dc.dataclass()
class ParamExp(WordPart):
    dollar: Pos
    rbrace: Pos

    short: bool  # $a instead of ${a}

    flags: Lit  # ${(flags)a} with [LANG_ZSH]

    # Only one of these is set at a time.
    # TODO(v4): perhaps use an Operator token here,
    # given how we've grown the number of booleans
    excl: bool    # ${!a}
    length: bool  # ${#a}
    width: bool   # mksh's ${%a}
    plus: bool    # ${+a} with [LANG_ZSH]

    # Only one of these is set at a time.
    # TODO(v4): consider joining Param and NestedParam into a single field,
    # even if that would be mildly annoying to non-Zsh users.
    param: Lit
    # A nested parameter expression in the form of [*ParamExp] or [*CmdSubst],
    # or either of those in a [*DblQuoted]. Only possible with [LANG_ZSH].
    nested_param: WordPart

    index: ArithmExpr # ${a[i]}, ${a["k"]}, or a ${a[i,j]} slice with [LANG_ZSH]

    # Only one of these is set at a time.
    # TODO(v4): consider joining these in a single "expansion" field/type,
    # because it should be impossible for multiple to be set at once,
    # and a flat structure like this takes up more space.
    modifiers: list[Lit]     # ${a:h2} with [LANG_ZSH]
    slice: Slice             # ${a:x:y}
    repl: Replace            # ${a/x/y}
    names: ParNamesOperator  # ${!prefix*} or ${!prefix@}
    exp: Expansion           # ${a:-b}, ${a#b}, etc

    # simple returns true if the parameter expansion is of the form $name or ${name},
    # only expanding a name without any further logic.
    def simple(self) -> bool:
        return (
            self.flags is None and
            not self.Excl and
            not self.Length and
            not self.Width and
            not self.Plus and
            self.nested_param is None and
            self.index is None and
            len(self.modifiers) == 0 and
            self.slice is None and
            self.repl is None and
            self.names == 0 and
            self.Exp is None
        )

    def pos(self) -> Pos:
        if self.dollar.is_valid():
            return self.dollar
        return self.param.pos()
        
    def end(self) -> Pos:
        if !self.short {
            return pos_add_col(self.rbrace, 1)
        # In short mode, we can only end in either an index or a simple name.
        if self.Index is not None:
            return pos_add_col(self.Index.End(), 1)
        return self.Param.End()

    func (self *ParamExp) nakedIndex() bool {
        # A naked index is arr[x] inside arithmetic, without a leading '$'.
        # In that case dollar is unset, unlike $arr[x] where it holds the '$' position.
        return self.short and self.Index is not None and !self.dollar.is_valid()


# Slice represents a character slicing expression inside a [ParamExp].
#
# This node will only appear with [LANG_BASH] and [LANG_MIR_BSD_KORN].
# [LANG_ZSH] uses a [BinaryArithm] with [Comma] in [ParamExp.Index] instead.
@dc.dataclass()
class Slice:
    offset: ArithmExpr
    length: ArithmExpr


# Replace represents a search and replace expression inside a [ParamExp].
@dc.dataclass()
class Replace:
    all: bool
    orig: Word
    with_: Word


# Expansion represents string manipulation in a [ParamExp] other than those
# covered by [Replace].
@dc.dataclass()
class Expansion:
    op: ParExpOperator
    word: Word
    

# ArithmExp represents an arithmetic expansion.
@dc.dataclass()
class ArithmExp(WordPart):
    left, right Pos
    Bracket     bool # deprecated $[expr] form
    Unsigned    bool # mksh's $((# expr))

    X ArithmExpr

    def pos(self) -> Pos:
        return a.left
    
    def end(self) -> Pos:
        if a.Bracket {
            return pos_add_col(a.right, 1)
        return pos_add_col(a.right, 2)


# ArithmCmd represents an arithmetic command.
#
# This node will only appear with [LANG_BASH] and [LANG_MIR_BSD_KORN].
@dc.dataclass()
class ArithmCmd(Command):
    left, right Pos
    Unsigned    bool # mksh's ((# expr))

    X ArithmExpr

    def pos(self) -> Pos:
        return a.left
    
    def end(self) -> Pos:
        return pos_add_col(a.right, 2)



# BinaryArithm represents a binary arithmetic expression.
#
# If Op is any assign operator, X will be a word with a single [*Lit] whose value
# is a valid name.
#
# Ternary operators like "a ? b : c" are fit into this structure. Thus, if
# Op==[TernQuest], Y will be a [*BinaryArithm] with Op==[TernColon].
# [TernColon] does not appear in any other scenario.
@dc.dataclass()
class BinaryArithm(ArithmExpr):
    op_pos Pos
    Op    BinAritOperator
    X, Y  ArithmExpr

    def pos(self) -> Pos:
        return b.X.Pos()
    
    def end(self) -> Pos:
        return b.Y.End()


# UnaryArithm represents an unary arithmetic expression. The unary operator
# may come before or after the sub-expression.
#
# If Op is [Inc] or [Dec], X will be a word with a single [*Lit] whose value is a
# valid name.
@dc.dataclass()
class UnaryArithm(ArithmExpr):
    op_pos Pos
    Op    UnAritOperator
    Post  bool
    X     ArithmExpr

    def pos(self) -> Pos:
        if u.Post {
            return u.X.Pos()
        return u.op_pos

    def end(self) -> Pos:
        if u.Post {
            return pos_add_col(u.op_pos, 2)
        return u.X.End()


# ParenArithm represents an arithmetic expression within parentheses.
@dc.dataclass()
class ParenArithm(ArithmExpr):
    lparen, rparen Pos

    X ArithmExpr

    def pos(self) -> Pos:
        return self.lparen
    
    def end(self) -> Pos:
        return pos_add_col(self.rparen, 1)


# FlagsArithm represents zsh subscript flags attached to an arithmetic expression,
# such as ${array[(flags)expr]}.
#
# This node will only appear with [LANG_ZSH].
@dc.dataclass()
class FlagsArithm(ArithmExpr):
    flags *Lit
    X     ArithmExpr

    def pos(self) -> Pos:
        return pos_add_col(z.flags.Pos(), -1)
    
    def end(self) -> Pos:
        if z.X is not None:
            return z.X.End()
        return pos_add_col(z.flags.End(), 1) # closing paren


# CaseClause represents a case (switch) clause.
@dc.dataclass()
class CaseClause(Command):
    Case, In, Esac Pos
    Braces         bool # deprecated mksh form with braces instead of in/esac

    Word  *Word
    items []*CaseItem
    last  []Comment

    def pos(self) -> Pos:
        return self.Case
    
    def end(self) -> Pos:
        return pos_add_col(self.Esac, 4)


# CaseItem represents a pattern list (case) within a [CaseClause].
@dc.dataclass()
class CaseItem(Node):
    Op       CaseOperator
    op_pos    Pos # unset if it was finished by "esac"
    Comments []Comment
    Patterns []*Word

    stmts []*Stmt
    last  []Comment

    def pos(self) -> Pos:
        return self.Patterns[0].Pos()
    
    def end(self) -> Pos:
        if self.op_pos.is_valid() {
            return pos_add_col(self.op_pos, len(self.Op.String()))
        return stmts_end(self.stmts, self.last)
"""  # noqa


# TestClause represents a Bash extended test clause.
#
# This node will only appear with [LANG_BASH] and [LANG_MIR_BSD_KORN].
@dc.dataclass()
class TestClause(Command):
    left: Pos
    right: Pos

    x: TestExpr

    def pos(self) -> Pos:
        return self.left

    def end(self) -> Pos:
        return pos_add_col(self.right, 2)



# BinaryTest represents a binary test expression.
@dc.dataclass()
class BinaryTest(TestExpr):
    op_pos: Pos
    op: BinTestOperator
    x: TestExpr
    y: TestExpr

    def pos(self) -> Pos:
        return self.x.pos()
    
    def end(self) -> Pos:
        return self.y.end()


# UnaryTest represents a unary test expression. The unary operator may come
# before or after the sub-expression.
@dc.dataclass()
class UnaryTest(TestExpr):
    op_pos: Pos
    op: UnTestOperator
    x: TestExpr

    def pos(self) -> Pos:
        return self.op_pos
    
    def end(self) -> Pos:
        return self.x.end()


# ParenTest represents a test expression within parentheses.
@dc.dataclass()
class ParenTest(TestExpr):
    lparen: Pos
    rparen: Pos

    x: TestExpr

    def pos(self) -> Pos:
        return self.lparen
    
    def end(self) -> Pos:
        return pos_add_col(self.rparen, 1)


# DeclClause represents a Bash declare clause.
#
# Args can contain a mix of regular and naked assignments. The naked
# assignments can represent either options or variable names.
#
# This node will only appear with [LANG_BASH].
@dc.dataclass()
class DeclClause(Command):
    # Variant is one of "declare", "local", "export", "readonly",
    # "typeset", or "nameref".
    variant: Lit
    args: list[Assign]

    def pos(self) -> Pos:
        return self.variant.pos()
    
    def end(self) -> Pos:
        if len(self.args) > 0:
            return self.args[-1].end()
        return self.variant.end()


# ArrayExpr represents a Bash array expression.
#
# This node will only appear with [LANG_BASH].
@dc.dataclass()
class ArrayExpr(Node):
    lparen: Pos
    rparen: Pos

    elems: list['ArrayElem']
    last: list[Comment]

    def pos(self) -> Pos:
        return self.lparen
    
    def end(self) -> Pos:
        return pos_add_col(self.rparen, 1)


# ArrayElem represents a Bash array element.
#
# Index can be nil; for example, declare -a x=(value).
# Value can be nil; for example, declare -A x=([index]=).
# Finally, neither can be nil; for example, declare -A x=([index]=value)
@dc.dataclass()
class ArrayElem(Node):
    index: ArithmExpr
    value: Word
    comments: list[Comment]

    def pos(self) -> Pos:
        if self.index is not None:
            return self.index.pos()
        return self.value.pos()

    def end(self) -> Pos:
        if self.value is not None:
            return self.value.end()
        return pos_add_col(self.index.pos(), 1)


# ExtGlob represents a Bash extended globbing expression. Note that these are
# parsed independently of whether or not `shopt -s extglob` has been used,
# as the parser runs statically and independently of any interpreter.
#
# This node will only appear with [LANG_BASH] and [LANG_MIR_BSD_KORN].
@dc.dataclass()
class ExtGlob(WordPart):
    op_pos: Pos
    op: GlobOperator
    pattern: Lit

    def pos(self) -> Pos:
        return self.op_pos
    
    def end(self) -> Pos:
        return pos_add_col(self.pattern.end(), 1)


# ProcSubst represents a Bash process substitution.
#
# This node will only appear with [LANG_BASH].
@dc.dataclass()
class ProcSubst(WordPart):
    op_pos: Pos
    rparen: Pos
    op: ProcOperator

    stmts: list[Stmt]
    last: list[Comment]

    def pos(self) -> Pos:
        return self.op_pos
    
    def end(self) -> Pos:
        return pos_add_col(self.rparen, 1)


# TimeClause represents a Bash time clause. PosixFormat corresponds to the -p
# flag.
#
# This node will only appear with [LANG_BASH] and [LANG_MIR_BSD_KORN].
@dc.dataclass()
class TimeClause(Command):
    time: Pos
    posix_format: bool
    stmt: Stmt

    def pos(self) -> Pos:
        return self.time
    
    def end(self) -> Pos:
        if self.stmt is None:
            return pos_add_col(self.time, 4)
        return self.stmt.end()


# CoprocClause represents a Bash coproc clause.
#
# This node will only appear with [LANG_BASH].
@dc.dataclass()
class CoprocClause(Command):
    coproc: Pos
    name: Word
    stmt: Stmt

    def pos(self) -> Pos:
        return self.coproc
    
    def end(self) -> Pos:
        return self.stmt.end()


# LetClause represents a Bash let clause.
#
# This node will only appear with [LANG_BASH] and [LANG_MIR_BSD_KORN].
@dc.dataclass()
class LetClause(Command):
    let: Pos
    exprs: list[ArithmExpr]

    def pos(self) -> Pos:
        return self.let
    
    def end(self) -> Pos:
        return self.exprs[-1].end()


# BraceExp represents a Bash brace expression, such as "{a,f}" or "{1..10}".
#
# This node will only appear as a result of [SplitBraces].
@dc.dataclass()
class BraceExp(WordPart):
    sequence: bool  # {x..y[..incr]} instead of {x,y[,...]}
    elems: list[Word]

    def pos(self) -> Pos:
        return pos_add_col(self.elems[0].pos(), -1)

    def end(self) -> Pos:
        return pos_add_col(word_last_end(self.elems), 1)


# TestDecl represents the declaration of a Bats test function.
@dc.dataclass()
class TestDecl(Command):
    position: Pos
    description: Word
    body: Stmt

    def pos(self) -> Pos:
        return self.position
    
    def end(self) -> Pos:
        return self.body.end()


def word_last_end(ws: list[Word]) -> Pos:
    if len(ws) == 0:
        return Pos()
    return ws[-1].end()
