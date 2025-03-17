# ruff: noqa: N802 N803
import typing as ta

from ... import check
from ...antlr import runtime as antlr4
from ...antlr.errors import SilentRaisingErrorListener
from . import nodes as no
from ._antlr.Protobuf3Lexer import Protobuf3Lexer  # type: ignore
from ._antlr.Protobuf3Parser import Protobuf3Parser  # type: ignore
from ._antlr.Protobuf3Visitor import Protobuf3Visitor  # type: ignore


##


class _ParseVisitor(Protobuf3Visitor):
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

    def visitField(self, ctx: Protobuf3Parser.FieldContext):
        name = ctx.fieldName().getText()
        type_: no.Type = check.isinstance(self.visitTypeRule(ctx.typeRule()), (no.SimpleType, no.TypeRef))
        num = int(ctx.fieldNumber().getText())
        repeated = ctx.REPEATED() is not None
        return no.Field(
            name=name,
            type=type_,
            num=num,
            repeated=repeated,
        )

    def visitMessage(self, ctx: Protobuf3Parser.MessageContext):
        name = ctx.messageName().getText()
        fields: list[no.Field] = []
        for mbc_ctx in ctx.messageBody().messageBodyContent():
            mbc = self.visitMessageBodyContent(mbc_ctx)
            if isinstance(mbc, no.Field):
                fields.append(mbc)
        return no.Message(
            name=name,
            fields=fields,
        )

    def visitMessageOrEnumType(self, ctx: Protobuf3Parser.MessageOrEnumTypeContext):
        return no.TypeRef(ctx.getText())

    def visitProto(self, ctx: Protobuf3Parser.ProtoContext):
        messages: list[no.Message] = []
        for ex_ctx in ctx.syntaxExtra():
            ex = self.visitSyntaxExtra(ex_ctx)
            if isinstance(ex, no.Message):
                messages.append(ex)
        return no.ProtoFile(
            messages=messages,
        )

    def visitSimpleType(self, ctx: Protobuf3Parser.SimpleTypeContext):
        return no.SimpleType(ctx.getText())


##


def create_parser(buf: str) -> Protobuf3Parser:
    lexer = Protobuf3Lexer(antlr4.InputStream(buf))
    lexer.removeErrorListeners()
    lexer.addErrorListener(SilentRaisingErrorListener())

    stream = antlr4.CommonTokenStream(lexer)
    stream.fill()

    parser = Protobuf3Parser(stream)
    parser.removeErrorListeners()
    parser.addErrorListener(SilentRaisingErrorListener())

    return parser


##


def parse_proto(buf: str, **kwargs: ta.Any) -> ta.Any:
    parser = create_parser(buf, **kwargs)
    node = _ParseVisitor().visit(parser.proto())
    return node
