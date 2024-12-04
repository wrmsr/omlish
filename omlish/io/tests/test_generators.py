from ... import lang
from .. import generators as gs


def test_prependable_generator_reader():
    def f():
        rdr = gs.PrependableStrGeneratorReader()

        i = yield from rdr.read(2)
        assert i == 'ab'

        rdr.prepend('c')
        i = yield from rdr.read(3)
        assert i == 'cde'

        rdr.prepend('gh')
        rdr.prepend('f')
        i = yield from rdr.read(2)
        assert i == 'fg'

        i = yield from rdr.read(2)
        assert i == 'hi'

        return 'done'

    cg = lang.corogen(f())
    assert cg.send() == cg.Yield(2)
    assert cg.send('ab') == cg.Yield(2)
    assert cg.send('de') == cg.Yield(1)
    assert cg.send('i') == cg.Return('done')


def test_buffered_generator_reader():
    def f():
        rdr = gs.BufferedStrGeneratorReader(4)

        i = yield from rdr.read(2)
        assert i == 'ab'

        i = yield from rdr.read(2)
        assert i == 'cd'

        i = yield from rdr.read(1)
        assert i == 'e'

        i = yield from rdr.read(2)
        assert i == 'fg'

        i = yield from rdr.read(2)
        assert i == 'hi'

        i = yield from rdr.read(8)
        assert i == 'jklmnopq'

        return 'done'

    cg = lang.corogen(f())
    assert cg.send() == cg.Yield(4)
    assert cg.send('abcd') == cg.Yield(4)
    assert cg.send('efgh') == cg.Yield(4)
    assert cg.send('ijkl') == cg.Yield(5)
    assert cg.send('mnopq') == cg.Return('done')
