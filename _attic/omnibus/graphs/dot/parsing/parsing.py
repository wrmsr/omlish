import typing as ta

from .... import antlr
from ...._vendor import antlr4
from ._antlr import DotLexer  # type: ignore
from ._antlr import DotParser  # type: ignore
from ._antlr import DotVisitor  # type: ignore


class _ParseVisitor(DotVisitor):
    pass


def parse(buf: str) -> ta.Any:
    lexer = DotLexer(antlr4.InputStream(buf))
    lexer.removeErrorListeners()
    lexer.addErrorListener(antlr.SilentRaisingErrorListener())

    stream = antlr4.CommonTokenStream(lexer)
    stream.fill()

    parser = DotParser(stream)
    parser.removeErrorListeners()
    parser.addErrorListener(antlr.SilentRaisingErrorListener())

    visitor = _ParseVisitor()
    return visitor.visit(parser.graph())
