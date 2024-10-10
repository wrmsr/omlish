from omlish.antlr import _runtime as antlr4  # noqa

from ._antlr.ChatLexer import ChatLexer  # type: ignore
from ._antlr.ChatParser import ChatParser  # type: ignore
from ._antlr.ChatVisitor import ChatVisitor  # type: ignore


class ChatVisitorImpl(ChatVisitor):

    def visitChildren(self, node):  # noqa
        print(node)
        return super().visitChildren(node)


def create_parser(buf: str) -> ChatParser:
    lexer = ChatLexer(antlr4.InputStream(buf))  # type: ignore

    stream = antlr4.CommonTokenStream(lexer)  # type: ignore
    stream.fill()

    parser = ChatParser(stream)

    return parser


CHAT = """
barf says: hi // comment0
// comment1
xarf says: /* comment2 */ xi
"""


def test_chat():
    parser = create_parser(CHAT)

    ChatVisitorImpl().visit(parser.chat())
