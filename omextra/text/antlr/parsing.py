# ruff: noqa: N802 N803
import typing as ta

from omlish import check

from . import runtime as antlr4
from .errors import SilentRaisingErrorListener


LexerT = ta.TypeVar('LexerT', bound=antlr4.Lexer)
ParserT = ta.TypeVar('ParserT', bound=antlr4.Parser)


##


def is_eof_context(ctx: antlr4.ParserRuleContext) -> bool:
    return ctx.getChildCount() == 1 and ctx.getChild(0).getSymbol().type == antlr4.Token.EOF


class StandardParseTreeVisitor(antlr4.ParseTreeVisitor):
    def visit(self, ctx: antlr4.ParserRuleContext):
        check.isinstance(ctx, antlr4.ParserRuleContext)
        return ctx.accept(self)

    def aggregateResult(self, aggregate, nextResult):  # noqa
        if aggregate is not None:
            check.none(nextResult)
            return aggregate
        else:
            check.none(aggregate)
            return nextResult


def make_parser(
        buf: str,
        lexer_cls: type[LexerT],
        parser_cls: type[ParserT],
        *,
        silent_errors: bool = False,
) -> ParserT:
    lexer = lexer_cls(antlr4.InputStream(buf))
    if silent_errors:
        lexer.removeErrorListeners()
        lexer.addErrorListener(SilentRaisingErrorListener())

    stream = antlr4.CommonTokenStream(lexer)
    stream.fill()

    parser = parser_cls(stream)
    if silent_errors:
        parser.removeErrorListeners()
        parser.addErrorListener(SilentRaisingErrorListener())

    return parser
