from .. import ops
from .. import parsing


def test_parsers() -> None:
    for p, s in [
        (ops.Concat(ops.StringLiteral('foo'), ops.StringLiteral('bar')), 'foobar'),
        (ops.Repeat(ops.Repeat.Times(3), ops.StringLiteral('ab')), 'ababab'),
    ]:
        print(p)
        print(repr(s))
        print(parsing.parse(p, s))
        print()
