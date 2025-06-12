import pytest

from ... import lang
from ..of_ import of
from ..values import ScalarTypedValue
from ..values import UniqueScalarTypedValue


class Foo(ScalarTypedValue[str]):
    pass


class Bar(UniqueScalarTypedValue[str]):
    pass


class Baz(UniqueScalarTypedValue[str], lang.Abstract):
    pass


class ABaz(Baz):
    pass


class BBaz(Baz):
    pass


def test_of():
    with of[Foo].collect(Foo('foo')).consume() as tvc:
        assert tvc.pop(Foo) == (Foo('foo'),)

    with of[Foo].collect(Foo('foo'), check_type=True).consume() as tvc:
        assert tvc.pop(Foo) == (Foo('foo'),)

    with of[Foo].consume(Foo('foo'), check_type=True) as tvc:
        assert tvc.pop(Foo) == (Foo('foo'),)

    with pytest.raises(TypeError):
        with of[Foo].consume(Foo('foo'), Bar('bar'), check_type=True):  # type: ignore[arg-type]  # FAILS
            pass

    with pytest.raises(TypeError):
        with of[Foo].consume(Foo('foo'), Bar('bar'), check_type=True):  # type: ignore[arg-type]  # FAILS
            pass
