import os.path

from ..._vendor import antlr4
from .._antlr import Protobuf3Lexer  # type: ignore
from .._antlr import Protobuf3Listener  # type: ignore
from .._antlr import Protobuf3Parser  # type: ignore


class Protobuf3PrintListener(Protobuf3Listener):

    def __init__(
            self,
            stream: antlr4.BufferedTokenStream.BufferedTokenStream,  # type: ignore
            parser: Protobuf3Parser
    ) -> None:
        super().__init__()
        self._stream = stream
        self._parser = parser

    def enterMessage(self, ctx: Protobuf3Parser.MessageContext):
        print(ctx)
        print(ctx.start.tokenIndex)
        for t in (self._stream.getHiddenTokensToRight(ctx.start.tokenIndex, 2) or []):
            print(t.text)

    def enterMessageBody(self, ctx: Protobuf3Parser.MessageBodyContext):
        print(ctx)
        print(ctx.start.tokenIndex)
        for t in (self._stream.getHiddenTokensToRight(ctx.start.tokenIndex, 2) or []):
            print(t.text)

    def enterField(self, ctx: Protobuf3Parser.FieldContext):
        print(ctx)
        print(ctx.start.tokenIndex)
        for t in (self._stream.getHiddenTokensToRight(ctx.start.tokenIndex, 2) or []):
            print(t.text)

    def enterTypeRule(self, ctx: Protobuf3Parser.TypeRuleContext):
        print(ctx)
        print(ctx.start.tokenIndex)
        for t in (self._stream.getHiddenTokensToRight(ctx.start.tokenIndex, 2) or []):
            print(t.text)


def test_proto():
    with open(os.path.join(os.path.dirname(__file__), 'examples/addressbook.proto'), 'r') as f:
        buf = f.read()
    lexer = Protobuf3Lexer(antlr4.InputStream(buf))
    stream = antlr4.CommonTokenStream(lexer)
    stream.fill()
    parser = Protobuf3Parser(stream)
    tree = parser.proto()
    printer = Protobuf3PrintListener(stream, parser)
    walker = antlr4.ParseTreeWalker()
    walker.walk(printer, tree)
