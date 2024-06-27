import pytest

from ..... import inject as inj
from ..harness import Harness
from ..harness import PytestScope


def test_pytest(harness):
    assert isinstance(harness, Harness)
    fr: pytest.FixtureRequest = harness[inj.tag(pytest.FixtureRequest, PytestScope.FUNCTION)]
    assert isinstance(fr, pytest.FixtureRequest)
    assert fr.function is test_pytest
