from ..core.types import AnyType
from ..core.types import Instance
from ..ops import typeof
from .helpers import make_mirror


def test_typeof():
    mirror = make_mirror()

    rty = typeof(list[int](), mirror=mirror)
    assert isinstance(rty, Instance)
    assert rty.type.runtime_object is list
    [arg] = rty.args
    assert isinstance(arg, AnyType)

    class MyList[T](list[T]):
        pass

    rty = typeof(MyList[int](), mirror=mirror)
    assert isinstance(rty, Instance)
    assert rty.type.runtime_object is MyList
    [arg] = rty.args
    assert isinstance(arg, Instance)
    assert arg.type.runtime_object is int
