import textwrap

from .. import parsing


def test_parsing():
    src = textwrap.dedent("""
    digraph G {
        a;
        b;
        a -> b;
    }
    """)
    parsing.parse(src)
