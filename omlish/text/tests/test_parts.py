from .. import parts as r


def test_rendering():
    print()
    for p in [
        'foo',
        ['foo', 'bar'],
        ['foo', r.Block(['bar', 'baz']), 'qux'],
        None,
    ]:
        print(p)
        print(r.render(p))  # type: ignore
        print()
