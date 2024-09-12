from ..resources import get_relative_resources


def test_relative_resources() -> None:
    rsrs = get_relative_resources('', globals=globals())
    assert 'test_relative_resources' in rsrs['test_resources.py'].read_bytes().decode()
