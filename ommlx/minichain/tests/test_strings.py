from ..content import Text
from ..strings import transform_strings


def test_transforms():
    assert transform_strings(lambda s: s + '!', Text('hello')) == Text('hello!')
