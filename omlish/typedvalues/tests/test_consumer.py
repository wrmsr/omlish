from ... import lang
from ..collection import TypedValues
from ..consumer import TypedValuesConsumer
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


def test_consumer():
    tvc: TypedValuesConsumer

    with TypedValuesConsumer(TypedValues(Foo('foo'))) as tvc:
        assert tvc.pop(Foo) == (Foo('foo'),)

    with TypedValuesConsumer(TypedValues(Bar('bar'))) as tvc:
        assert tvc.pop(Bar) == Bar('bar')

    with TypedValuesConsumer(TypedValues(ABaz('abaz'))) as tvc:
        assert tvc.pop(Baz) == ABaz('abaz')

    with TypedValuesConsumer(TypedValues(ABaz('abaz'))) as tvc:
        assert tvc.pop(ABaz) == ABaz('abaz')
