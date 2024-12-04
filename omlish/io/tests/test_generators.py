from .. import generators as gs


def test_reader0():
    def f():
        rdr = gs.PrependableStrGeneratorReader()
        yield from rdr.read(2)

    g = f()
    assert next(g) == 2
