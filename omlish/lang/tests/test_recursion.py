import pytest

from ..recursion import LimitedRecursionError
from ..recursion import recursion_limiting


def test_recursion():
    @recursion_limiting(5)
    def foo(x):
        return x + foo(x - 1) if x > 0 else 0

    assert foo(4) == 4 + 3 + 2 + 1

    with pytest.raises(LimitedRecursionError):
        foo(5)


def test_recursion_depth_validation():
    """Regression test: recursion limiting should correctly track and validate recursion depth.

    This test verifies that the fix for the bug in the depth validation logic
    (changing 'if not isinstance(pd, int) and pd > 0:' to 'if not isinstance(pd, int) or pd <= 0:')
    allows normal recursion limiting to work correctly.
    """

    @recursion_limiting(10)
    def bar(x):
        if x <= 0:
            return 'done'
        return bar(x - 1)

    # Normal recursive calls should work
    assert bar(5) == 'done'
    assert bar(9) == 'done'

    # Hitting the limit should raise LimitedRecursionError
    with pytest.raises(LimitedRecursionError):
        bar(10)

    # Verify we can still make normal calls after hitting the limit
    assert bar(5) == 'done'
