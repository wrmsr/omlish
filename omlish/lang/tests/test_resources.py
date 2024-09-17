import json
import typing as ta

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
        assert 'class Abstract' in rsrs['abstract.py'].read_bytes().decode()

        src = get_relative_resources('...', **kwargs)['.manifests.json'].read_bytes()
        assert isinstance(json.loads(src.decode('utf-8')), list)
