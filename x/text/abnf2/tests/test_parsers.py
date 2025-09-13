def test_parsers() -> None:
    for p, s in [
        (Concat(StringLiteral('foo'), StringLiteral('bar')), 'foobar'),
        (Repeat(Repeat.Times(3), StringLiteral('ab')), 'ababab'),
    ]:
        print(p)
        print(repr(s))
        print(parse(p, s))
        print()
