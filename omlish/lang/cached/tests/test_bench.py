"""
TODO:
 - riic - https://github.com/python/cpython/commit/1c858c352b8c11419f79f586334c49378726dba8 ~3.5

functools.lru_cache:
11.8 ns ± 0.0532 ns per loop (mean ± std. dev. of 7 runs, 100,000,000 loops each)

lang.cached_function:
75.1 ns ± 0.141 ns per loop (mean ± std. dev. of 7 runs, 10,000,000 loops each)
"""
import functools

from ..function import cached_function


def test_bench():
    def f():
        return 42

    assert f() == 42

    f0 = cached_function(f)
    f1 = functools.cache(f)

    assert f0() == 42
    assert f1() == 42

    for _ in range(3):
        assert f0() == 42
        assert f1() == 42
