from .. import base as ba
from .. import ops


def test_parsers() -> None:
    for p, s in [
        (ops.Concat(ops.StringLiteral('foo'), ops.StringLiteral('bar')), 'foobar'),
        (ops.Repeat(ops.Repeat.Times(3), ops.StringLiteral('ab')), 'ababab'),
    ]:
        print(p)
        print(repr(s))
        print(ba.parse(p, s))
        print()
