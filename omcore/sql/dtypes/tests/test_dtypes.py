from .... import marshal as msh
from ..dtypes import Datetime
from ..dtypes import Dtype
from ..dtypes import Integer
from ..dtypes import String
from ..dtypes import Uuid


def test_singletons():
    assert Integer() is Integer()
    assert String() is String()
    assert Datetime() is Datetime()
    assert Uuid() is Uuid()


def test_marshal_roundtrip():
    for dt in [Integer(), String(), Datetime(), Uuid()]:
        v = msh.marshal(dt, Dtype)
        assert msh.unmarshal(v, Dtype) == dt
