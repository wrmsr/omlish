from .. import parts as tp


def test_rendering():
    print()
    for p in [
        'foo',
        ['foo', 'bar'],
        ['foo', tp.Block(['bar', 'baz']), 'qux'],
        None,
    ]:
        print(p)
        print(tp.render(p))  # type: ignore
        print()
