import pytest

from ...testing import pytest as ptu
from ..asts import ArgsRenderer
from .asts import check_foo


@ptu.skip.if_cant_import('executing')
def test_check_equal():
    assert ArgsRenderer.smoketest()

    with pytest.raises(ValueError):  # noqa
        check_foo()
