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
TODO: original go:

func (p *Parser) arithmExpr(compact bool) ArithmExpr {
    return p.arithmExprComma(compact)
}

# These function names are inspired by Bash's expr.c

func (p *Parser) arithmExprComma(compact bool) ArithmExpr {
    return p.arithmExprBinary(compact, p.arithmExprAssign, Comma)
}

func (p *Parser) arithmExprLor(compact bool) ArithmExpr {
    return p.arithmExprBinary(compact, p.arithmExprLand, OrArit, XorBool)
}

func (p *Parser) arithmExprLand(compact bool) ArithmExpr {
    return p.arithmExprBinary(compact, p.arithmExprBor, AndArit)
}

func (p *Parser) arithmExprBor(compact bool) ArithmExpr {
    return p.arithmExprBinary(compact, p.arithmExprBxor, Or)
}

func (p *Parser) arithmExprBxor(compact bool) ArithmExpr {
    return p.arithmExprBinary(compact, p.arithmExprBand, Xor)
}

func (p *Parser) arithmExprBand(compact bool) ArithmExpr {
    return p.arithmExprBinary(compact, p.arithmExprEquality, And)
}

func (p *Parser) arithmExprEquality(compact bool) ArithmExpr {
    return p.arithmExprBinary(compact, p.arithmExprComparison, Eql, Neq)
}

func (p *Parser) arithmExprComparison(compact bool) ArithmExpr {
    return p.arithmExprBinary(compact, p.arithmExprShift, Lss, Gtr, Leq, Geq)
}

func (p *Parser) arithmExprShift(compact bool) ArithmExpr {
    return p.arithmExprBinary(compact, p.arithmExprAddition, Shl, Shr)
}

func (p *Parser) arithmExprAddition(compact bool) ArithmExpr {
    return p.arithmExprBinary(compact, p.arithmExprMultiplication, Add, Sub)
}

func (p *Parser) arithmExprMultiplication(compact bool) ArithmExpr {
    return p.arithmExprBinary(compact, p.arithmExprPower, Mul, Quo, Rem)
}
"""  # noqa
import typing as ta

from .langs import LANG_ZSH
from .langs import lang_in
from .nodes import RECOVERED_POS
from .nodes import ArithmExpr
from .nodes import BinaryArithm
from .nodes import Lit
from .nodes import ParamExp
from .nodes import ParenArithm
from .nodes import Pos
from .nodes import UnaryArithm
from .nodes import Word
from .tokens import BinAritOperator
from .tokens import Token
from .tokens import UnAritOperator


if ta.TYPE_CHECKING:
    from .parser import Parser


##


# compact specifies whether we allow spaces between expressions.
# This is true for let
def arithm_expr(p: 'Parser', compact: bool) -> ArithmExpr | None:
    return arithm_expr_comma(p, compact)


# These function names are inspired by Bash's expr.c

def arithm_expr_comma(p: 'Parser', compact: bool) -> ArithmExpr | None:
    return arithm_expr_binary(p, compact, arithm_expr_assign, BinAritOperator.COMMA)


def arithm_expr_assign(p: 'Parser', compact: bool) -> ArithmExpr | None:
    # Assign is different from the other binary operators because it's
    # right-associative and needs to check that it's placed after a name
    value = arithm_expr_ternary(p, compact)
    try:
        op = BinAritOperator(p.tok)
    except ValueError:
        return value
    if op in (
        BinAritOperator.ADD_ASSGN, BinAritOperator.SUB_ASSGN, BinAritOperator.MUL_ASSGN,
        BinAritOperator.QUO_ASSGN, BinAritOperator.REM_ASSGN, BinAritOperator.AND_ASSGN,
        BinAritOperator.OR_ASSGN, BinAritOperator.XOR_ASSGN, BinAritOperator.SHL_ASSGN,
        BinAritOperator.SHR_ASSGN, BinAritOperator.ASSGN,
        BinAritOperator.AND_BOOL_ASSGN, BinAritOperator.OR_BOOL_ASSGN,
        BinAritOperator.XOR_BOOL_ASSGN, BinAritOperator.POW_ASSGN,
    ):
        if compact and p.spaced:
            return value
        if not is_arith_name(value):
            p.pos_err(p.pos, '%s must follow a name', p.tok)
        pos = p.pos
        tok = p.tok
        next_arith_op(p, compact)
        y = arithm_expr_assign(p, compact)
        if y is None:
            p.follow_err_exp(pos, tok)
        return BinaryArithm(
            op_pos=pos,
            op=BinAritOperator(tok),
            x=value,
            y=y,
        )
    return value


def arithm_expr_ternary(p: 'Parser', compact: bool) -> ArithmExpr | None:
    value = arithm_expr_lor(p, compact)
    try:
        op = BinAritOperator(p.tok)
    except ValueError:
        return value
    if op != BinAritOperator.TERN_QUEST or (compact and p.spaced):
        return value

    if value is None:
        p.cur_err('%s must follow an expression', p.tok)
    quest_pos = p.pos
    next_arith_op(p, compact)
    try:
        op2 = BinAritOperator(p.tok)
    except ValueError:
        op2 = None
    if op2 == BinAritOperator.TERN_COLON:
        p.follow_err_exp(quest_pos, BinAritOperator.TERN_QUEST)
    true_expr = arithm_expr(p, compact)
    if true_expr is None:
        p.follow_err_exp(quest_pos, BinAritOperator.TERN_QUEST)
    try:
        op3 = BinAritOperator(p.tok)
    except ValueError:
        op3 = None
    if op3 != BinAritOperator.TERN_COLON:
        p.pos_err(quest_pos, 'ternary operator missing %s after %s', Token.COLON, Token.QUEST)
    colon_pos = p.pos
    next_arith_op(p, compact)
    false_expr = arithm_expr_ternary(p, compact)
    if false_expr is None:
        p.follow_err_exp(colon_pos, BinAritOperator.TERN_COLON)
    return BinaryArithm(
        op_pos=quest_pos,
        op=BinAritOperator.TERN_QUEST,
        x=value,
        y=BinaryArithm(
            op_pos=colon_pos,
            op=BinAritOperator.TERN_COLON,
            x=true_expr,
            y=false_expr,
        ),
    )


def arithm_expr_lor(p: 'Parser', compact: bool) -> ArithmExpr | None:
    return arithm_expr_binary(p, compact, arithm_expr_land, BinAritOperator.OR_ARIT, BinAritOperator.XOR_BOOL)


def arithm_expr_land(p: 'Parser', compact: bool) -> ArithmExpr | None:
    return arithm_expr_binary(p, compact, arithm_expr_bor, BinAritOperator.AND_ARIT)


def arithm_expr_bor(p: 'Parser', compact: bool) -> ArithmExpr | None:
    return arithm_expr_binary(p, compact, arithm_expr_bxor, BinAritOperator.OR)


def arithm_expr_bxor(p: 'Parser', compact: bool) -> ArithmExpr | None:
    return arithm_expr_binary(p, compact, arithm_expr_band, BinAritOperator.XOR)


def arithm_expr_band(p: 'Parser', compact: bool) -> ArithmExpr | None:
    return arithm_expr_binary(p, compact, arithm_expr_equality, BinAritOperator.AND)


def arithm_expr_equality(p: 'Parser', compact: bool) -> ArithmExpr | None:
    return arithm_expr_binary(p, compact, arithm_expr_comparison, BinAritOperator.EQL, BinAritOperator.NEQ)


def arithm_expr_comparison(p: 'Parser', compact: bool) -> ArithmExpr | None:
    return arithm_expr_binary(
        p, compact, arithm_expr_shift,
        BinAritOperator.LSS, BinAritOperator.GTR, BinAritOperator.LEQ, BinAritOperator.GEQ,
    )


def arithm_expr_shift(p: 'Parser', compact: bool) -> ArithmExpr | None:
    return arithm_expr_binary(p, compact, arithm_expr_addition, BinAritOperator.SHL, BinAritOperator.SHR)


def arithm_expr_addition(p: 'Parser', compact: bool) -> ArithmExpr | None:
    return arithm_expr_binary(p, compact, arithm_expr_multiplication, BinAritOperator.ADD, BinAritOperator.SUB)


def arithm_expr_multiplication(p: 'Parser', compact: bool) -> ArithmExpr | None:
    return arithm_expr_binary(p, compact, arithm_expr_power, BinAritOperator.MUL, BinAritOperator.QUO, BinAritOperator.REM)  # noqa


def arithm_expr_power(p: 'Parser', compact: bool) -> ArithmExpr | None:
    # Power is different from the other binary operators because it's right-associative
    value = arithm_expr_unary(p, compact)
    try:
        op = BinAritOperator(p.tok)
    except ValueError:
        return value
    if op != BinAritOperator.POW or (compact and p.spaced):
        return value

    if value is None:
        p.cur_err('%s must follow an expression', p.tok)

    tok = p.tok
    pos = p.pos
    next_arith_op(p, compact)
    y = arithm_expr_power(p, compact)
    if y is None:
        p.follow_err_exp(pos, tok)
    return BinaryArithm(
        op_pos=pos,
        op=BinAritOperator(tok),
        x=value,
        y=y,
    )


def arithm_expr_unary(p: 'Parser', compact: bool) -> ArithmExpr | None:
    if not compact:
        p.got(Token.NEWL_)

    try:
        op = UnAritOperator(p.tok)
    except ValueError:
        op = None
    if op in (UnAritOperator.NOT, UnAritOperator.BIT_NEGATION, UnAritOperator.PLUS, UnAritOperator.MINUS):
        ue = UnaryArithm(op_pos=p.pos, op=UnAritOperator(p.tok))
        next_arith_op(p, compact)
        ue.x = arithm_expr_unary(p, compact)
        if ue.x is None:
            p.follow_err_exp(ue.op_pos, ue.op)
        return ue
    return arithm_expr_value(p, compact)


def arithm_expr_value(p: 'Parser', compact: bool) -> ArithmExpr | None:
    x: ArithmExpr | None = None
    if p.tok in (Token.ADD_ADD, Token.SUB_SUB):
        ue = UnaryArithm(op_pos=p.pos, op=UnAritOperator(p.tok))
        next_arith(p, compact)
        if p.tok != Token.LIT_WORD_:
            p.follow_err(ue.op_pos, ue.op, 'a literal')
        ue.x = arithm_expr_value(p, compact)
        return ue
    elif p.tok == Token.LEFT_PAREN:
        if p.quote == p._PARAM_EXP_ARITHM and lang_in(p.lang, LANG_ZSH):
            x = p.zsh_sub_flags()
        else:
            pe = ParenArithm(lparen=p.pos)
            next_arith_op(p, compact)
            pe.x = follow_arithm(p, Token.LEFT_PAREN, pe.lparen)
            pe.rparen = p.matched(pe.lparen, Token.LEFT_PAREN, Token.RIGHT_PAREN)
            if p.quote == p._PARAM_EXP_ARITHM and p.tok == Token.LIT_WORD_:
                p.check_lang(pe.lparen, LANG_ZSH, 'subscript flags')
            x = pe
    elif p.tok == Token.LEFT_BRACK:
        p.cur_err('%s must follow a name', p.tok)
    elif p.tok == Token.COLON:
        p.cur_err('ternary operator missing %s before %s', Token.QUEST, Token.COLON)
    elif p.tok == Token.LIT_WORD_:
        l = p.get_lit()
        if p.tok != Token.LEFT_BRACK:
            x = p.word_one(l)
        else:
            pe2 = ParamExp(short=True, param=l)
            pe2.index = p.either_index()
            x = p.word_one(pe2)
    elif (
        (cond_bck := (p.tok == Token.BCK_QUOTE))
        or (cond_default := True)  # noqa: F841
    ):
        if cond_bck:
            if p.quote == p._ARITHM_EXPR_LET and p.open_bquotes > 0:
                return None
            # fallthrough to default
        w = p.get_word()
        if w is not None:
            x = w
        else:
            return None

    if compact and p.spaced:
        return x
    if not compact:
        p.got(Token.NEWL_)

    if p.tok == Token.ADD_ADD or p.tok == Token.SUB_SUB:
        if not is_arith_name(x):
            p.cur_err('%s must follow a name', p.tok)
        u = UnaryArithm(
            post=True,
            op_pos=p.pos,
            op=UnAritOperator(p.tok),
            x=x,
        )
        next_arith(p, compact)
        return u
    return x


# nextArith consumes a token.
# It returns true if compact and the token was followed by spaces
def next_arith(p: 'Parser', compact: bool) -> bool:
    p.next()
    if compact and p.spaced:
        return True
    if not compact:
        p.got(Token.NEWL_)
    return False


def next_arith_op(p: 'Parser', compact: bool) -> None:
    pos = p.pos
    tok = p.tok
    if next_arith(p, compact):
        p.follow_err_exp(pos, tok)


# arithmExprBinary is used for all left-associative binary operators
def arithm_expr_binary(
        p: 'Parser',
        compact: bool,
        next_op: ta.Callable[['Parser', bool], ArithmExpr | None],
        *operators: BinAritOperator,
) -> ArithmExpr | None:
    value = next_op(p, compact)
    while True:
        found_op: BinAritOperator | None = None
        for op in operators:
            if p.tok == op.value:
                found_op = op
                break

        if found_op is None or (compact and p.spaced):
            return value

        if value is None:
            p.cur_err('%s must follow an expression', p.tok)

        pos = p.pos
        next_arith_op(p, compact)
        y = next_op(p, compact)
        if y is None:
            p.follow_err_exp(pos, found_op)

        value = BinaryArithm(
            op_pos=pos,
            op=found_op,
            x=value,
            y=y,
        )


def is_arith_name(left: ArithmExpr | None) -> bool:
    if not isinstance(left, Word):
        return False
    if len(left.parts) != 1:
        return False
    wp = left.parts[0]
    if isinstance(wp, Lit):
        from .parser import valid_name
        return valid_name(wp.value)
    elif isinstance(wp, ParamExp):
        return wp.naked_index()
    else:
        return False


def follow_arithm(p: 'Parser', ftok: Token, fpos: Pos) -> ArithmExpr | None:
    x = arithm_expr(p, False)
    if x is None:
        p.follow_err_exp(fpos, ftok)
    return x


def peek_arithm_end(p: 'Parser') -> bool:
    return p.tok == Token.RIGHT_PAREN and p.r == ')'


def arithm_matching_err(p: 'Parser', pos: Pos, left: Token, right: Token) -> None:
    if p.tok in (Token.LIT_, Token.LIT_WORD_):
        p.cur_err('not a valid arithmetic operator: %s', p.val)
    elif p.tok == Token.LEFT_BRACK:
        p.cur_err('%s must follow a name', Token.LEFT_BRACK)
    elif p.tok == Token.COLON:
        p.cur_err('ternary operator missing %s before %s', Token.QUEST, Token.COLON)
    elif p.tok in (Token.RIGHT_PAREN, Token.EOF_):
        p.matching_err(pos, left, right)
    elif p.tok == Token.PERIOD:
        p.check_lang(p.pos, LANG_ZSH, 'floating point arithmetic')
    else:
        if p.quote & p._ALL_ARITHM_EXPR != 0:
            p.cur_err('not a valid arithmetic operator: %s', p.tok)
        p.matching_err(pos, left, right)


def matched_arithm(p: 'Parser', lpos: Pos, left: Token, right: Token) -> None:
    if not p.got(right):
        arithm_matching_err(p, lpos, left, right)


def arithm_end(p: 'Parser', ltok: Token, lpos: Pos, old: ta.Any) -> Pos:
    if not peek_arithm_end(p):
        if p.recover_error():
            return RECOVERED_POS
        arithm_matching_err(p, lpos, ltok, Token.DBL_RIGHT_PAREN)
    p.rune()
    p.post_nested(old)
    pos = p.pos
    p.next()
    return pos
