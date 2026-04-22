import typing as ta

import pytest

from .... import lang
from .... import marshal as msh
from .... import typedvalues as tv


class Opt(tv.TypedValue, lang.Abstract, lang.Sealed):
    pass


class OptA(Opt, tv.ScalarTypedValue[int]):
    pass


class OptB(Opt, tv.ScalarTypedValue[str]):
    pass


class OptC(Opt, tv.ScalarTypedValue[str]):
    pass


class OtherOpt(tv.ScalarTypedValue[str], lang.Final):
    pass


def test_marshal_abstract():
    tvs = tv.TypedValues(OptA(420), OptB('abc'))

    mtvs: ta.Any = msh.marshal(tvs, tv.TypedValues[Opt])
    tvs2 = msh.unmarshal(mtvs, tv.TypedValues[Opt])
    assert list(tvs2) == list(tvs)

    tvs2 = msh.unmarshal([*mtvs, {'opt_c': 'ghi'}], tv.TypedValues[Opt])
    assert list(tvs2) == [*tvs, OptC('ghi')]

    with pytest.raises(KeyError):
        msh.unmarshal([*mtvs, {'other_opt': 'huh'}], tv.TypedValues[Opt])


def test_marshal_union():
    tvs = tv.TypedValues(OptA(420), OptB('abc'))

    mtvs: ta.Any = msh.marshal(tvs, tv.TypedValues[OptA | OptB])
    tvs2 = msh.unmarshal(mtvs, tv.TypedValues[OptA | OptB])
    assert list(tvs2) == list(tvs)

    with pytest.raises(KeyError):
        msh.unmarshal([*mtvs, {'opt_c': 'ghi'}], tv.TypedValues[OptA | OptB])


def test_marshal_union2():
    tvs = tv.TypedValues(OptA(420), OptB('abc'), OtherOpt('huh'))

    mtvs: ta.Any = msh.marshal(tvs, tv.TypedValues[OptA | OptB | OtherOpt])
    tvs2 = msh.unmarshal(mtvs, tv.TypedValues[OptA | OptB | OtherOpt])
    assert list(tvs) == list(tvs2)

    with pytest.raises(KeyError):
        msh.unmarshal([*mtvs, {'opt_c': 'ghi'}], tv.TypedValues[OptA | OptB])
