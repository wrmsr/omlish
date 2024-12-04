from ... import lang
from .. import generators as gs


def test_reader0():
    def f():
        rdr = gs.PrependableStrGeneratorReader()
        i = yield from rdr.read(2)
        assert i == 'ab'
        return 'done'

    cg = lang.corogen(f())
    assert cg.send() == cg.Yield(2)
    assert cg.send('ab') == cg.Return('done')
