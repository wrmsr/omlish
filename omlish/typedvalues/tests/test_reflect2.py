import typing as ta

from ... import lang
from ..reflect2 import reflect2_typed_values_impls
from ..values import TypedValue


class TvA(TypedValue):
    pass


class TvB(TvA):
    pass


class TvC(TvA):
    pass


class TvD(TypedValue):
    pass


class TvE(TypedValue, lang.Abstract, lang.Sealed):
    pass


class TvF(TvE):
    pass


class TvG(TvE):
    pass


def test_reflect2():
    obj: ta.Any
    for obj in [
        TvA,
        TvE,
        TvA | TvE,
    ]:
        print()
        print(obj)

        lst = reflect2_typed_values_impls(
            obj,
            find_abstract_subclasses=True,
        )
        print(lst)
