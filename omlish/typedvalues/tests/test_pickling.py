import pickle

from ..collection import TypedValues
from ..values import ScalarTypedValue


class Foo(ScalarTypedValue[int]):
    pass


class Bar(ScalarTypedValue[int]):
    pass


def test_pickling():
    for i in range(2):
        tvs = TypedValues[Foo | Bar](Foo(1), Foo(2), Bar(i))
        tvs2 = pickle.loads(pickle.dumps(tvs))  # noqa
        assert set(tvs) == set(tvs2)

    assert not TypedValues()
    assert not pickle.loads(pickle.dumps(TypedValues()))  # noqa
