from omlish import marshal as msh

from ..json import JsonValue


def test_marshal_json():
    m = msh.marshal({'abc': 420}, JsonValue)
    assert m == {'abc': 420}
