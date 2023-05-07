from .. import check

import pytest


def test_check():
    check.none(None)


def test_one_of():
    assert check.one_of(1, None) == 1
    assert check.one_of(None, 1) == 1

    with pytest.raises(ValueError):
        check.one_of()
    with pytest.raises(ValueError):
        check.one_of(1, 1)
    with pytest.raises(ValueError):
        check.one_of(None, None)

    assert check.one_of(None, default=1) == 1
    assert check.one_of(None, default_factory=lambda: 1) == 1

    assert check.one_of(1, 0) == 1
    with pytest.raises(ValueError):
        check.one_of(0)
    assert check.one_of(0, not_none=True) == 0
