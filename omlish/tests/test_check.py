import pytest

from .. import check


def test_check():
    with pytest.raises(ValueError):  # noqa
        check.equal(1, 2)
