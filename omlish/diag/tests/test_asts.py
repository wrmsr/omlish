import pytest

from ...testing import pytest as ptu
from ..asts import ArgsRenderer


def check_equal(l, r):
    if l != r:
        ra = ArgsRenderer().render_args(l, r)
        if ra is None:
            raise TypeError
        lr, rr = ra
        msg = f'{lr} != {rr}'
        raise ValueError(msg)


@ptu.skip_if_cant_import('executing')
def test_check_equal():
    assert ArgsRenderer.smoketest()

    def foo(x):
        return x + 1

    with pytest.raises(ValueError):  # noqa
        check_equal(foo(3) + 2, 8)
