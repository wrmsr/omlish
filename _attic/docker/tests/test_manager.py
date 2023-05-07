import pytest

from ...inject.dev import pytest as ptinj
from ..dev.pytest import DockerManager


@pytest.mark.no_ci
@pytest.mark.docker
def test_manager(harness: ptinj.Harness):
    man = harness[DockerManager]
    cli = man.client
    assert cli is not None
