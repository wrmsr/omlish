import pytest

from .. import matchfns as mf


##


def test_matchfns():
    mf0: mf.MatchFn[[int], str] = mf.simple(lambda i: i == 0, lambda _: 'zero!')
    assert mf0(0) == 'zero!'
    with pytest.raises(mf.MatchGuardError):
        mf0(1)

    mf1: mf.MatchFn[[int], str] = mf.simple(lambda i: i == 1, lambda _: 'one!')
    assert mf1(1) == 'one!'
    with pytest.raises(mf.MatchGuardError):
        mf1(0)

    mf0b: mf.MatchFn[[int], str] = mf.simple(lambda i: i == 0, lambda _: 'zero again!')
    assert mf0b(0) == 'zero again!'
    with pytest.raises(mf.MatchGuardError):
        mf0b(1)

    mmf0: mf.MatchFn[[int], str] = mf.multi(mf0, mf1, mf0b)
    assert mmf0(0) == 'zero!'
    assert mmf0(1) == 'one!'
    with pytest.raises(mf.MatchGuardError):
        mmf0(2)

    mmf1: mf.MatchFn[[int], str] = mf.multi(mf0, mf1, mf0b, strict=True)
    with pytest.raises(mf.AmbiguousMatchesError):
        mmf1(0)
    assert mmf1(1) == 'one!'
    with pytest.raises(mf.MatchGuardError):
        mmf1(2)
