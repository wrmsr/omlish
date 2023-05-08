import string
import typing as ta

from ... import check
from ... import collections as col
from ... import dataclasses as dc
from ... import properties


class Op(dc.Enum, abstract=True, reorder=True):
    GLYPH_WORD_SEP: ta.ClassVar[str] = '_'
    GLYPH_WORD_CHARS: ta.ClassVar[ta.AbstractSet[str]] = {*string.ascii_lowercase, GLYPH_WORD_SEP}

    glyph: str

    dc.validate(lambda glyph: not set(glyph) & set(string.whitespace))

    @properties.cached
    def is_word(self) -> bool:
        return not (set(self.glyph) - Op.GLYPH_WORD_CHARS)

    @properties.cached
    def glyph_parts(self) -> ta.Sequence[str]:
        return self.glyph.split(Op.GLYPH_WORD_SEP)


class BinOp(dc.ValueEnum, Op):
    pass


class BinOps(BinOp.Values):
    ADD = BinOp('+')
    SUB = BinOp('-')
    MUL = BinOp('*')
    DIV = BinOp('/')
    MOD = BinOp('%')

    BIT_AND = BinOp('&')
    BIT_OR = BinOp('|')
    BIT_XOR = BinOp('^')

    LSH = BinOp('<<')
    RSH = BinOp('>>')

    FLOOR_DIV = BinOp('//')
    POW = BinOp('**')
    MAT_MUL = BinOp('@')


class BoolOp(dc.ValueEnum, Op):
    pass


class BoolOps(BoolOp.Values):
    AND = BoolOp('and')
    OR = BoolOp('or')


class CmpOp(dc.ValueEnum, Op):
    pass


class CmpOps(CmpOp.Values):
    EQ = CmpOp('==')
    NE = CmpOp('!=')
    GT = CmpOp('>')
    GE = CmpOp('>=')
    LT = CmpOp('<')
    LE = CmpOp('<=')

    IS = CmpOp('is')
    IS_NOT = CmpOp('is_not')

    IN = CmpOp('in')
    NOT_IN = CmpOp('not_in')


class UnaryOp(dc.ValueEnum, Op):
    pass


class UnaryOps(UnaryOp.Values):
    PLUS = UnaryOp('+')
    MINUS = UnaryOp('-')
    INVERT = UnaryOp('~')

    NOT = UnaryOp('not')


OPS_BY_GLYPH_BY_CLS: ta.Mapping[ta.Type[Op], ta.Mapping[str, Op]] = {
    c: col.unique_dict((o.glyph, o) for n in ns for o in [check.isinstance(ns(n), Op)])
    for c, ns in [
        (BinOp, BinOps),
        (BoolOp, BoolOps),
        (CmpOp, CmpOps),
        (UnaryOp, UnaryOps),
    ]
}
