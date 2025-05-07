# ruff: noqa: N802 N803
from . import runtime as antlr4


##


class ParseError(Exception):
    pass


class SilentRaisingErrorListener(antlr4.ErrorListener):
    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        raise ParseError(recognizer, offendingSymbol, line, column, msg, e)
