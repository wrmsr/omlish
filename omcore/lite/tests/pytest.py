import typing as ta


##


pytest: ta.Any

try:
    import pytest

except ImportError:
    pytest = None

    def pytest_mark(name, *args, **kwargs):
        return lambda fn: fn

else:
    def pytest_mark(name, *args, **kwargs):
        def inner(fn):
            return getattr(pytest.mark, name)(*args, **kwargs)(fn)
        return inner
