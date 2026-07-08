"""
TODO:
 - IPv4Network / IPv6Network
 - unions
"""
import sys
import typing as ta

from ... import dataclasses as dc
from ... import lang
from ... import reflect2 as rfl
from ..api.contexts import MarshalContext
from ..api.contexts import MarshalFactoryContext
from ..api.contexts import UnmarshalContext
from ..api.contexts import UnmarshalFactoryContext
from ..api.types import Marshaler
from ..api.types import MarshalerFactory
from ..api.types import Unmarshaler
from ..api.types import UnmarshalerFactory
from ..api.values import Value


with lang.auto_proxy_import(globals()):
    import ipaddress


##


class IpaddressMarshaler(Marshaler):
    def marshal(self, ctx: MarshalContext, o: ta.Any) -> Value:
        return str(o)


@dc.dataclass(frozen=True)
class IpaddressUnmarshaler(Unmarshaler):
    ty: type

    def unmarshal(self, ctx: UnmarshalContext, v: Value) -> ta.Any:
        return self.ty(v)


#


_IP_ADDRESS_TYPES: set[type] | None = None


def _get_ipaddress_types() -> set[type] | None:
    global _IP_ADDRESS_TYPES
    if (ts := _IP_ADDRESS_TYPES) is not None:
        return ts

    if 'ipaddress' not in sys.modules:
        return None

    ts = _IP_ADDRESS_TYPES = {
        ipaddress.IPv4Address,
        ipaddress.IPv6Address,
    }

    return ts


class IpaddressMarshalerFactory(MarshalerFactory):
    def make_marshaler(self, ctx: MarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], Marshaler] | None:
        if not (
                (cls := rfl.get_runtime_type_or_none(rty)) is not None and
                (ts := _get_ipaddress_types()) is not None and
                cls in ts
        ):
            return None

        return lambda: IpaddressMarshaler()


class IpaddressUnmarshalerFactory(UnmarshalerFactory):
    def make_unmarshaler(self, ctx: UnmarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], Unmarshaler] | None:
        if not (
                (cls := rfl.get_runtime_type_or_none(rty)) is not None and
                (ts := _get_ipaddress_types()) is not None and
                cls in ts
        ):
            return None

        return lambda: IpaddressUnmarshaler(cls)


IPADDRESS_MARSHALER_FACTORY = IpaddressMarshalerFactory()
IPADDRESS_UNMARSHALER_FACTORY = IpaddressUnmarshalerFactory()
