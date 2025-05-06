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


def test_buffered_coro_reader():
    def f():
        rdr = gs.BufferedStrCoroReader(4)

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

    cg = lang.capture_coroutine(f())
    assert cg.send() == cg.Yield(4)
    assert cg.send('abcd') == cg.Yield(4)
    assert cg.send('efgh') == cg.Yield(4)
    assert cg.send('ijkl') == cg.Yield(5)
    assert cg.send('mnopq') == cg.Return('done')
