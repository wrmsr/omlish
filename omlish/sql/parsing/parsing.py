# ruff: noqa: N802 N803
import typing as ta

from ... import check
from ...antlr import runtime as antlr4
from ...antlr.delimit import DelimitingLexer
from ...antlr.errors import SilentRaisingErrorListener
from .. import queries as no
from ._antlr.MinisqlLexer import MinisqlLexer  # type: ignore
from ._antlr.MinisqlParser import MinisqlParser  # type: ignore
from ._antlr.MinisqlVisitor import MinisqlVisitor  # type: ignore


##


class _ParseVisitor(MinisqlVisitor):
    def visit(self, ctx: antlr4.ParserRuleContext):
        check.isinstance(ctx, antlr4.ParserRuleContext)
        node = ctx.accept(self)
        return node

    def aggregateResult(self, aggregate, nextResult):
        if aggregate is not None:
            check.none(nextResult)
            return aggregate
        else:
            check.none(aggregate)
            return nextResult

    #

    def visitExprSelectItem(self, ctx: MinisqlParser.ExprSelectItemContext):
        value = self.visit(ctx.expr())
        label = self.visit(ctx.ident()) if ctx.ident() is not None else None
        return no.SelectItem(value, label)

    def visitIntegerNumber(self, ctx: MinisqlParser.IntegerNumberContext):
        return no.Literal(int(ctx.INTEGER_VALUE().getText()))

    def visitPrimarySelect(self, ctx: MinisqlParser.PrimarySelectContext):
        items = [self.visit(i) for i in ctx.selectItem()]
        relations = [self.visit(r) for r in ctx.relation()]
        where = self.visit(ctx.where) if ctx.where is not None else None
        return no.Select(
            items=items,
            from_=check.single(relations) if relations else None,
            where=where,
        )

    def visitQuotedIdent(self, ctx: MinisqlParser.QuotedIdentContext):
        name = unquote(ctx.QUOTED_IDENT().getText(), '"')
        return no.Ident(name)

    def visitUnquotedIdent(self, ctx: MinisqlParser.UnquotedIdentContext):
        return no.Ident(ctx.getText())


##


def create_parser(buf: str) -> MinisqlParser:
    lexer = MinisqlLexer(antlr4.InputStream(buf))
    lexer.removeErrorListeners()
    lexer.addErrorListener(SilentRaisingErrorListener())

    stream = antlr4.CommonTokenStream(lexer)
    stream.fill()

    parser = MinisqlParser(stream)
    parser.removeErrorListeners()
    parser.addErrorListener(SilentRaisingErrorListener())

    return parser


##


def parse_stmt(buf: str, **kwargs) -> no.Stmt:
    parser = create_parser(buf, **kwargs)
    node = _ParseVisitor().visit(parser.singleStmt())
    return check.isinstance(node, no.Stmt)


class _DelimitingLexer(DelimitingLexer, MinisqlLexer):
    pass


def split_stmts(buf: str) -> ta.Sequence[str]:
    lexer = _DelimitingLexer(
        antlr4.InputStream(buf),
        delimiter_token=MinisqlParser.DELIMITER,
        delimiters=[';'],
    )
    lexer.removeErrorListeners()
    lexer.addErrorListener(SilentRaisingErrorListener())

    lst, part = lexer.split()
    if part.strip():
        raise ValueError(part)

    return [s for s, _ in lst]


def parse_stmts(buf: str, **kwargs) -> ta.Sequence[no.Stmt]:
    return [parse_stmt(sb, **kwargs) for sb in split_stmts(buf)]


##


def quote(val: str, q: str) -> str:
    return q + val.replace(q, q * 2) + q


def unquote(val: str, q: str) -> str:
    check.arg(val.startswith(q) and val.endswith(q))
    return val[1:-1].replace(q * 2, q)
