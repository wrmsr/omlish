import typing as ta

import pytest

from ... import lang
from ... import marshal as msh
from ..collection import TypedValues
from ..values import ScalarTypedValue
from ..values import TypedValue


class Opt(TypedValue, lang.Sealed, lang.Abstract):
    pass


class OptA(Opt, ScalarTypedValue[int]):
    pass


class OptB(Opt, ScalarTypedValue[str]):
    pass


class OptC(Opt, ScalarTypedValue[str]):
    pass


class OtherOpt(ScalarTypedValue[str], lang.Final):
    pass


def test_marshal_abstract():
    tvs = TypedValues(OptA(420), OptB('abc'))

    mtvs: ta.Any = msh.marshal(tvs, TypedValues[Opt])
    tvs2 = msh.unmarshal(mtvs, TypedValues[Opt])
    assert list(tvs2) == list(tvs)

    tvs2 = msh.unmarshal([*mtvs, {'opt_c': 'ghi'}], TypedValues[Opt])
    assert list(tvs2) == [*tvs, OptC('ghi')]

    with pytest.raises(KeyError):
        msh.unmarshal([*mtvs, {'other_opt': 'huh'}], TypedValues[Opt])


def test_marshal_union():
    tvs = TypedValues(OptA(420), OptB('abc'))

    mtvs: ta.Any = msh.marshal(tvs, TypedValues[OptA | OptB])
    tvs2 = msh.unmarshal(mtvs, TypedValues[OptA | OptB])
    assert list(tvs2) == list(tvs)

    with pytest.raises(KeyError):
        msh.unmarshal([*mtvs, {'opt_c': 'ghi'}], TypedValues[OptA | OptB])


def test_marshal_union2():
    tvs = TypedValues(OptA(420), OptB('abc'), OtherOpt('huh'))

    mtvs: ta.Any = msh.marshal(tvs, TypedValues[OptA | OptB | OtherOpt])
    tvs2 = msh.unmarshal(mtvs, TypedValues[OptA | OptB | OtherOpt])
    assert list(tvs) == list(tvs2)

    with pytest.raises(KeyError):
        msh.unmarshal([*mtvs, {'opt_c': 'ghi'}], TypedValues[OptA | OptB])
