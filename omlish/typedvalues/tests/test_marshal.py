from ... import lang
from ... import marshal as msh
from ..collection import TypedValues
from ..values import ScalarTypedValue
from ..values import TypedValue


class Opt(TypedValue, lang.Abstract):
    pass


class OptA(Opt, ScalarTypedValue[int]):
    pass


class OptB(Opt, ScalarTypedValue[str]):
    pass


def test_marshal():
    tvs = TypedValues(OptA(420), OptB('abc'))
    mtvs = msh.marshal(tvs, TypedValues[Opt])
    print(mtvs)
    tvs2 = msh.unmarshal(mtvs, TypedValues[Opt])
    print(tvs2)
    assert list(tvs) == list(tvs2)
