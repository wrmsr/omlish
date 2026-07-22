import json
import typing as ta

import pytest

from ..resources import get_relative_resources


def test_relative_resources() -> None:
    kwargs: ta.Any
    for kwargs in [
        {'package': __package__},
        {'file': __file__},
    ]:
        rsrs = get_relative_resources(**kwargs)
        assert 'test_relative_resources' in rsrs['test_resources.py'].read_bytes().decode()

        rsrs = get_relative_resources('..', **kwargs)
        assert 'get_relative_resources' in rsrs['resources.py'].read_bytes().decode()

        rsrs = get_relative_resources('..classes', **kwargs)
        assert 'is_abstract_class' in rsrs['abstract.py'].read_bytes().decode()

        src = get_relative_resources('...', **kwargs)['.om-manifests.json'].read_bytes()
        assert isinstance(json.loads(src.decode('utf-8')), list)


def test_relative_resources_beyond_top_level():
    # __package__ is 3 packages deep - 3 levels up would escape the top-level package.
    with pytest.raises(ValueError):  # noqa
        get_relative_resources('....', package=__package__)
