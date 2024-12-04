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

        rdr.prepend('f')
        rdr.prepend('gh')
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
