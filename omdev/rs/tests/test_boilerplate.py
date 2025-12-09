import pytest


def test_boilerplate():
    try:
        from .. import _boilerplate
    except ImportError:
        pytest.skip('rust boilerplate module not built', allow_module_level=True)

    assert _boilerplate.sum_as_string(1, 2) == '3'  # type: ignore
