"""
Has to be outside of test_*.py files or pytest rewrites them for assert tracking, confusing the ast machinery.
"""
from ..asts import ArgsRenderer


def check_equal(l, r):
    if l != r:
        ra = ArgsRenderer().render_args(l, r)
        if ra is None:
            raise TypeError
        lr, rr = ra
        msg = f'{lr} != {rr}'
        raise ValueError(msg)


def foo(x):
    return x + 1


def check_foo():
    check_equal(foo(3) + 2, 8)
