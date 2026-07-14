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
