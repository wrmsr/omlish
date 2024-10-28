from ... import lang
from ..params import LinearParamsPreparer
from ..params import NamedParamsPreparer
from ..params import NumericParamsPreparer


def test_linear():
    pp = LinearParamsPreparer('?')
    assert pp.add(1) == '?'
    assert pp.add('foo') == '?'
    assert pp.add(1) == '?'
    assert pp.add(2) == '?'
    assert pp.add('foo') == '?'
    assert pp.add('bar') == '?'
    assert pp.prepare() == lang.Args(
        1,
        'foo',
        1,
        2,
        'foo',
        'bar',
    )


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


def test_named():
    pp = NamedParamsPreparer(NamedParamsPreparer.render_named)
    assert pp.add(1) == ':_0'
    assert pp.add('foo') == ':foo'
    assert pp.add(1) == ':_0'
    assert pp.add(2) == ':_1'
    assert pp.add('foo') == ':foo'
    assert pp.add('bar') == ':bar'
    assert pp.prepare() == lang.Args(
        _0=1,
        foo='foo',
        _1=2,
        bar='bar',
    )
