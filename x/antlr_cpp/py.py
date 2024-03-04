import typing as ta

import antlr4

from ._py.ChatLexer import ChatLexer
from ._py.ChatParser import ChatParser


def create_parser(buf: str) -> ChatParser:
    lexer = ChatLexer(antlr4.InputStream(buf))

    stream = antlr4.CommonTokenStream(lexer)
    stream.fill()

    parser = ChatParser(stream)

    return parser


def _main():
    with open('test.chat', 'r') as f:
        buf = f.read()

    parser = create_parser(buf)

    print(parser)


if __name__ == '__main__':
    _main()
