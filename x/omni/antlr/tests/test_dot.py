import textwrap

from .. import antlr
from .. import dot as adot
from ...graphs.dot import dot
from ._antlr import ChatLexer  # type: ignore
from ._antlr import ChatParser  # type: ignore


def test_dot():
    buf = textwrap.dedent("""
    barf says: hi // comment0
    // comment1
    xarf says: /* comment2 */ xi
    """).lstrip()

    parsed = antlr.parse(buf, ChatLexer, ChatParser)

    gv = dot.render(adot.dot_ctx(parsed.chat()))

    print(gv)

    # dot.open_dot(gv)
