from ..harness import Harness


def test_pytest(harness):
    assert isinstance(harness, Harness)
    assert harness.function().function is test_pytest
