from ..params import LinearParamsPreparer
from ..params import NamedParamsPreparer
from ..params import NumericParamsPreparer
from ..params import substitute_params


def test_linear():
    pp = LinearParamsPreparer('?')
    assert pp.add(1) == '?'
    assert pp.add('foo') == '?'
    assert pp.add(1) == '?'
    assert pp.add(2) == '?'
    assert pp.add('foo') == '?'
    assert pp.add('bar') == '?'
    assert list(px := pp.prepare()) == [
        1,
        'foo',
        1,
        2,
        'foo',
        'bar',
    ]

    assert substitute_params(px, {
        1: 123,
        'bar': 'bar!',
        2: 456,
        'foo': 'foo!',
    }) == [
        123,
        'foo!',
        123,
        456,
        'foo!',
        'bar!',
    ]


def test_numeric():
    pp = NumericParamsPreparer()
    assert pp.add(1) == ':1'
    assert pp.add('foo') == ':2'
    assert pp.add(1) == ':1'
    assert pp.add(2) == ':3'
    assert pp.add('foo') == ':2'
    assert pp.add('bar') == ':4'
    assert list(pp.prepare()) == [
        1,
        'foo',
        2,
        'bar',
    ]


def test_named():
    pp = NamedParamsPreparer(NamedParamsPreparer.render_named)
    assert pp.add(1) == ':_0'
    assert pp.add('foo') == ':foo'
    assert pp.add(1) == ':_0'
    assert pp.add(2) == ':_1'
    assert pp.add('foo') == ':foo'
    assert pp.add('bar') == ':bar'
    assert (px := pp.prepare()) == dict(
        _0=1,
        foo='foo',
        _1=2,
        bar='bar',
    )

    assert substitute_params(px, {
        1: 123,
        'bar': 'bar!',
        2: 456,
        'foo': 'foo!',
    }) == dict(
        _0=123,
        foo='foo!',
        _1=456,
        bar='bar!',
    )
