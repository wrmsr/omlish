import typing as ta

from omlish import check
from omlish.antlr import runtime as antlr4
from omlish.antlr.delimit import DelimitingLexer
from omlish.antlr.parsing import SilentRaisingErrorListener

from . import nodes as no
from ._antlr.MiniSqlLexer import MiniSqlLexer
from ._antlr.MiniSqlParser import MiniSqlParser
from ._antlr.MiniSqlVisitor import MiniSqlVisitor


##


class _ParseVisitor(MiniSqlVisitor):
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


##


def create_parser(buf: str) -> MiniSqlParser:
    lexer = MiniSqlLexer(antlr4.InputStream(buf))
    lexer.removeErrorListeners()
    lexer.addErrorListener(SilentRaisingErrorListener())

    stream = antlr4.CommonTokenStream(lexer)
    stream.fill()

    parser = MiniSqlParser(stream)
    parser.removeErrorListeners()
    parser.addErrorListener(SilentRaisingErrorListener())

    return parser


##


def parse_stmt(buf: str, **kwargs) -> no.Stmt:
    parser = create_parser(buf, **kwargs)
    node = _ParseVisitor().visit(parser.singleStatement())
    return check.isinstance(node, no.Stmt)


class _DelimitingLexer(DelimitingLexer, MiniSqlLexer):
    pass


def split_stmts(buf: str) -> ta.Sequence[str]:
    lexer = _DelimitingLexer(
        antlr4.InputStream(buf),
        delimiter_token=MiniSqlParser.DELIMITER,
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
