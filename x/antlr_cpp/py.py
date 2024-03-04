"""
(barf says: hi \n\nxarf says:  xi\n<EOF> (barf says: hi \n (barf  barf  ) (says:  says :  ) (hi  hi  ) \n) (\n \n) (xarf says:  xi\n (xarf  xarf  ) (says:  says :  ) ( xi   xi) \n) <EOF>)
(barf says: hi \n (barf  barf  ) (says:  says :  ) (hi  hi  ) \n)
(barf  barf  )
(says:  says :  )
(hi  hi  )
(\n \n)
(xarf says:  xi\n (xarf  xarf  ) (says:  says :  ) ( xi   xi) \n)
(xarf  xarf  )
(says:  says :  )
( xi   xi)

[]
[18]
[25 18]
[26 18]
[27 18]
[18]
[18]
[25 18]
[26 18]
[27 18]
"""
import typing as ta

import antlr4

from ._py.ChatLexer import ChatLexer
from ._py.ChatParser import ChatParser
from ._py.ChatVisitor import ChatVisitor


class ChatVisitorImpl(ChatVisitor):

    def visitChildren(self, node):
        print(node)
        return super().visitChildren(node)


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

    ChatVisitorImpl().visit(parser.chat())


if __name__ == '__main__':
    _main()
