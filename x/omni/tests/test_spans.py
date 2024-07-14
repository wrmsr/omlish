from .. import spans as s


def test_aligned_range():
    assert list(s.aligned_range(s.Span(s.Marker(3, s.Bound.EXACTLY), s.Marker(4, s.Bound.EXACTLY)), 3)) == [
        s.Span(s.Marker(3, s.Bound.EXACTLY), s.Marker(4, s.Bound.EXACTLY)),
    ]

    assert list(s.aligned_range(s.Span(s.Marker(3, s.Bound.EXACTLY), s.Marker(4, s.Bound.EXACTLY)), 3)) == [
        s.Span(s.Marker(3, s.Bound.EXACTLY), s.Marker(4, s.Bound.EXACTLY)),
    ]

    assert list(s.aligned_range(s.Span(s.Marker(3, s.Bound.EXACTLY), s.Marker(6, s.Bound.EXACTLY)), 3)) == [
        s.Span(s.Marker(3, s.Bound.EXACTLY), s.Marker(6, s.Bound.BELOW)),
        s.Span(s.Marker(6, s.Bound.EXACTLY), s.Marker(6, s.Bound.EXACTLY)),
    ]

    assert list(s.aligned_range(s.Span(s.Marker(2, s.Bound.EXACTLY), s.Marker(13, s.Bound.EXACTLY)), 3)) == [
        s.Span(s.Marker(2, s.Bound.EXACTLY), s.Marker(3, s.Bound.BELOW)),
        s.Span(s.Marker(3, s.Bound.EXACTLY), s.Marker(6, s.Bound.BELOW)),
        s.Span(s.Marker(6, s.Bound.EXACTLY), s.Marker(9, s.Bound.BELOW)),
        s.Span(s.Marker(9, s.Bound.EXACTLY), s.Marker(12, s.Bound.BELOW)),
        s.Span(s.Marker(12, s.Bound.EXACTLY), s.Marker(13, s.Bound.EXACTLY)),
    ]


def test_str():
    assert str(s.Span(s.Marker(5, s.Bound.EXACTLY), s.Marker(10, s.Bound.BELOW))) == '[5,10)'


def test_dicts():
    s0 = s.Span.of(0, 'EXACTLY', 4, 'BELOW')
    d = s0.to_dict()
    s1 = s.Span.from_dict(d)
    assert s0 == s1


def test_parse():
    assert s.Span.parse('(a,b]') == s.Span(s.Marker('a', s.Bound.ABOVE), s.Marker('b', s.Bound.EXACTLY))
    assert s.Span.parse('[a,...)') == s.Span(s.Marker('a', s.Bound.EXACTLY), s.Marker.UNBOUNDED_BELOW)
    assert s.Span.parse('(...,...)') == s.Span.UNBOUNDED


def test_is_empty():
    assert not s.Span.parse('[a,a]').is_empty
    assert not s.Span.parse('[a,...)').is_empty
    assert not s.Span.parse('(...,a]').is_empty
    assert not s.Span.parse('(...,...)').is_empty
    assert s.Span.parse('(a,a)').is_empty
