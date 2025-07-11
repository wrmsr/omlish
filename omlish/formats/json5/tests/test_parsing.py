import pytest

from ..errors import Json5Error
from ..parsing import parse_many


def test_parse_many():
    assert list(parse_many('')) == []
    assert list(parse_many('{}')) == [{}]
    assert list(parse_many('{}{}')) == [{}, {}]
    assert list(parse_many('{"x": []}{"y": []}')) == [{'x': []}, {'y': []}]
    assert list(parse_many('{}\n{}')) == [{}, {}]
    assert list(parse_many('\n{}\n{}\n')) == [{}, {}]
    assert list(parse_many('\n  {}  \n  {}\n')) == [{}, {}]

    for s in [
        ',',
        '{},{}',
    ]:
        with pytest.raises(Json5Error):
            list(parse_many(s))
