"""
TODO:
 - NaN, Infinity, -Infinity
"""
import dataclasses as dc
import textwrap
import typing as ta

from omlish import lang

from .antlr_dev import _runtime as antlr4  # noqa
from .antlr_dev.tests._antlr.JsonLexer import JsonLexer  # noqa
from .antlr_dev.tests._antlr.JsonParser import JsonParser  # noqa
from .antlr_dev.tests._antlr.JsonVisitor import JsonVisitor  # noqa


T = ta.TypeVar('T')
V = ta.TypeVar('V')


##


@dc.dataclass(frozen=True)
class TaggedValue(lang.Final, ta.Generic[V, T]):
    v: V
    t: T


##


@dc.dataclass(frozen=True)
class Location(lang.Final):
    line: int
    column: int
    offset: int


@dc.dataclass(frozen=True)
class Span(lang.Final):
    start: Location
    stop: Location


##


JsonValue: ta.TypeAlias = ta.Union[
    str,
    int,
    float,
    bool,
    None,
    list['JsonValue'],
    dict[str, 'JsonValue'],
]


##


def _make_span(ctx: antlr4.ParserRuleContext) -> Span:  # noqa
    return Span(
        start=Location(
            line=ctx.start.line,
            column=ctx.start.column,
            offset=ctx.start.start,
        ),
        stop=Location(
            line=ctx.stop.line,
            column=ctx.stop.column,
            offset=ctx.stop.stop,
        ),
    )


def _unquote(s: str) -> str:
    if s[0] != '"' or s[-1] != '"':
        raise ValueError(s)
    return s[1:-1]


class JsonVisitorImpl(JsonVisitor):

    def visitObj(self, ctx: JsonParser.ObjContext):
        d = {}
        for p in ctx.pair():
            k, v = self.visit(p)
            d[k] = v
        return TaggedValue(d, _make_span(ctx))

    def visitPair(self, ctx: JsonParser.PairContext):
        return (
            self.visit(ctx.key()),
            self.visit(ctx.value()),
        )

    def visitKey(self, ctx: JsonParser.KeyContext):
        return TaggedValue(_unquote(ctx.getText()), _make_span(ctx))

    def visitArray(self, ctx: JsonParser.ArrayContext):
        vs = []
        for v in ctx.value():
            vs.append(self.visit(v))
        return TaggedValue(vs, _make_span(ctx))

    def visitValue(self, ctx: JsonParser.ValueContext):
        if (s := ctx.STRING()) is not None:
            return TaggedValue(_unquote(s.getText()), _make_span(ctx))

        elif (n := ctx.NUMBER()) is not None:
            ns = n.getText()
            try:
                v = int(ns)
            except ValueError:
                v = float(ns)
            return TaggedValue(v, _make_span(ctx))

        elif ctx.TRUE() is not None:
            return TaggedValue(True, _make_span(ctx))

        elif ctx.FALSE() is not None:
            return TaggedValue(False, _make_span(ctx))

        elif ctx.NULL() is not None:
            return TaggedValue(None, _make_span(ctx))

        else:
            return super().visitValue(ctx)


def parse(buf: str) -> TaggedValue[JsonValue, Span]:
    lexer = JsonLexer(antlr4.InputStream(buf))
    stream = antlr4.CommonTokenStream(lexer)
    stream.fill()
    parser = JsonParser(stream)

    visitor = JsonVisitorImpl()
    return visitor.visit(parser.json())


def _main() -> None:
    s = textwrap.dedent("""
    {
        "name": "Alice",
        "age": 30,
        "is_student": false,
        "courses": ["Mathematics", "Physics", "Computer Science"],
        "address": {
            "street": "123 Main St",
            "city": "Wonderland",
            "zip_code": "12345"
        },
        "grades": {
            "Mathematics": "A",
            "Physics": "B+",
            "Computer Science": "A-"
        },
        "emergency_contact": null
    }
    """)
    print(parse(s))


if __name__ == '__main__':
    _main()
