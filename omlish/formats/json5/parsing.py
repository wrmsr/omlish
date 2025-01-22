# ruff: noqa: N802
import typing as ta

from omlish import antlr

from ._antlr.Json5Lexer import Json5Lexer  # type: ignore
from ._antlr.Json5Parser import Json5Parser  # type: ignore
from ._antlr.Json5Visitor import Json5Visitor  # type: ignore
from .errors import Json5Error
from .literals import LITERAL_VALUES
from .literals import parse_number_literal
from .literals import parse_string_literal


class Json5ParseVisitor(antlr.parsing.StandardParseTreeVisitor, Json5Visitor):
    def visitArr(self, ctx: Json5Parser.ArrContext):
        return [self.visit(e) for e in ctx.value()]

    def visitKey(self, ctx: Json5Parser.KeyContext):
        if (s := ctx.STRING()) is not None:
            return parse_string_literal(s.getText())

        elif (i := ctx.IDENTIFIER()) is not None:
            return parse_string_literal(''.join(['"', i.getText(), '"']))

        elif (l := ctx.LITERAL()) is not None:
            return LITERAL_VALUES[l.getText()]

        elif (n := ctx.NUMERIC_LITERAL()) is not None:
            return n.getText()

        else:
            raise RuntimeError(ctx)

    def visitNumber(self, ctx: Json5Parser.NumberContext):
        return parse_number_literal(ctx.getText())

    def visitObj(self, ctx: Json5Parser.ObjContext):
        dct: dict[ta.Any, ta.Any] = {}
        for pair in ctx.pair():
            key, value = self.visit(pair)
            dct[key] = value
        return dct

    def visitPair(self, ctx: Json5Parser.PairContext):
        key = self.visit(ctx.key())
        value = self.visit(ctx.value())
        return (key, value)

    def visitValue(self, ctx: Json5Parser.ValueContext):
        if (s := ctx.STRING()) is not None:
            return parse_string_literal(s.getText())

        elif (n := ctx.LITERAL()) is not None:
            return LITERAL_VALUES[n.getText()]

        else:
            return super().visitChildren(ctx)


def parse(buf: str) -> ta.Any:
    try:
        parser = antlr.parsing.make_parser(
            buf,
            Json5Lexer,
            Json5Parser,
            silent_errors=True,
        )

        root = parser.json5()

    except antlr.errors.ParseError as e:
        raise Json5Error from e

    if antlr.parsing.is_eof_context(root):
        raise Json5Error('Empty input')

    visitor = Json5ParseVisitor()
    return visitor.visit(root)
