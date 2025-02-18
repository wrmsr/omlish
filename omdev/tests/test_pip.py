import pytest

from ..pip import lookup_latest_package_version


@pytest.mark.online
def test_lookup_latest_package_version():
    v = lookup_latest_package_version('omlish')
    assert v
