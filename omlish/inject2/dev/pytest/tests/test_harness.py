import pytest

from ..harness import Harness


@pytest.mark.skip('inj2 -> inj')
def test_pytest(harness):
    assert isinstance(harness, Harness)
