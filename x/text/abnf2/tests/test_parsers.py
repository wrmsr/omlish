from .. import base as ba
from .. import parsers as pa


def test_parsers() -> None:
    for p, s in [
        (pa.Concat(pa.StringLiteral('foo'), pa.StringLiteral('bar')), 'foobar'),
        (pa.Repeat(pa.Repeat.Times(3), pa.StringLiteral('ab')), 'ababab'),
    ]:
        print(p)
        print(repr(s))
        print(ba.parse(p, s))
        print()
