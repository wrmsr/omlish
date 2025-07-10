import pytest

from ..clicli import _parse_latest_version_str


def test_parse_latest_version_str():
    for s in [
        '0',
        '0.0',
        '0.0.0',
        '0.0.0.dev350',
    ]:
        assert _parse_latest_version_str(s) == s

    for s in [
        'a',
        '0.',
        '0.0.0.0',  # noqa
        '; echo lol',
    ]:
        with pytest.raises(ValueError):  # noqa
            _parse_latest_version_str(s)
