from .... import lang
from .. import readers as gs


def test_prependable_coro_reader():
    def f():
        rdr = gs.PrependableStrCoroReader()

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

    cg = lang.capture_coroutine(f())
    assert cg.send() == cg.Yield(2)
    assert cg.send('ab') == cg.Yield(2)
    assert cg.send('de') == cg.Yield(1)
    assert cg.send('i') == cg.Return('done')
