import re
import textwrap

from .. import dotenv as dotenv_


def test_dotenv():
    parser = dotenv_.Parser(textwrap.dedent("""
    a=b
    c=d
    """))

    parser.read_pattern(re.compile(r'\s*'))
    m0 = parser.read_pattern(re.compile(r'\w+=\w+'))
    parser.read_pattern(re.compile(r'\s*'))
    m1 = parser.read_pattern(re.compile(r'\w+=\w+'))

    assert m0 is not None
    assert m1 is not None
