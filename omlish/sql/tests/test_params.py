from ... import lang
from ..params import NumericParamsPreparer


def test_numeric():
    pp = NumericParamsPreparer()
    assert pp.add(1) == ':1'
    assert pp.add('foo') == ':2'
    assert pp.add(1) == ':1'
    assert pp.add(2) == ':3'
    assert pp.add('foo') == ':2'
    assert pp.add('bar') == ':4'
    assert pp.prepare() == lang.Args(
        1,
        'foo',
        2,
        'bar',
    )
