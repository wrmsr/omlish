from ..harness import Harness


def test_pytest(harness):
    assert isinstance(harness, Harness)
