import pytest


def test_boilerplate():
    try:
        from .. import _boilerplate
        if not getattr(_boilerplate, '__file__'):
            raise ImportError  # noqa
    except ImportError:
        pytest.skip('rust boilerplate module not built')

    assert _boilerplate.sum_as_string(1, 2) == '3'  # type: ignore
