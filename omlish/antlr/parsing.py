# ruff: noqa: N802 N803
import typing as ta

from . import runtime as antlr4


LexerT = ta.TypeVar('LexerT', bound=antlr4.Lexer)
ParserT = ta.TypeVar('ParserT', bound=antlr4.Parser)


def parse(
        buf: str,
        lexer_cls: type[LexerT],
        parser_cls: type[ParserT],
) -> ParserT:
    lexer = lexer_cls(antlr4.InputStream(buf))
    stream = antlr4.CommonTokenStream(lexer)
    stream.fill()
    return parser_cls(stream)
