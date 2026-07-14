import decimal
import fractions
import typing as ta

from ... import check
from ..api.contexts import MarshalContext
from ..api.contexts import UnmarshalContext
from ..api.types import Marshaler
from ..api.types import Unmarshaler
from ..api.values import Value
from ..factories.typemap import TypeMapMarshalerFactory
from ..factories.typemap import TypeMapUnmarshalerFactory


##


class ComplexMarshalerUnmarshaler(Marshaler, Unmarshaler):
    def marshal(self, ctx: MarshalContext, o: complex) -> Value:
        return [o.real, o.imag]

    def unmarshal(self, ctx: UnmarshalContext, v: Value) -> ta.Any:
        real, imag = check.isinstance(v, list)
        return complex(real, imag)


class DecimalMarshalerUnmarshaler(Marshaler, Unmarshaler):
    def marshal(self, ctx: MarshalContext, o: decimal.Decimal) -> Value:
        return str(o)

    def unmarshal(self, ctx: UnmarshalContext, v: Value) -> ta.Any:
        return decimal.Decimal(check.isinstance(v, str))


class FractionMarshalerUnmarshaler(Marshaler, Unmarshaler):
    def marshal(self, ctx: MarshalContext, o: fractions.Fraction) -> Value:
        return [o.numerator, o.denominator]

    def unmarshal(self, ctx: UnmarshalContext, v: Value) -> ta.Any:
        num, denom = check.isinstance(v, list)
        return fractions.Fraction(num, denom)


NUMBERS_MARSHALER_FACTORY = TypeMapMarshalerFactory({
    complex: ComplexMarshalerUnmarshaler(),
    decimal.Decimal: DecimalMarshalerUnmarshaler(),
    fractions.Fraction: FractionMarshalerUnmarshaler(),
})

NUMBERS_UNMARSHALER_FACTORY = TypeMapUnmarshalerFactory({
    complex: ComplexMarshalerUnmarshaler(),
    decimal.Decimal: DecimalMarshalerUnmarshaler(),
    fractions.Fraction: FractionMarshalerUnmarshaler(),
})
