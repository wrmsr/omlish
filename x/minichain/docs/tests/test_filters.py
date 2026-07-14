from ... import docs as D  # noqa


def test_filters():
    assert str(D.f('foo')) == ':foo'
    assert str(D.eq(D.f('foo'), 1) & D.le(D.f('bar'), 2)) == '(:foo = 1 && :bar <= 2)'
    assert str(D.in_(D.f('barf'), 1, 2, 3)) == '(:barf = 1 || :barf = 2 || :barf = 3)'
