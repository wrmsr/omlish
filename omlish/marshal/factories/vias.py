import typing as ta

from ... import metadata as md
from ... import reflect as rfl
from ..api.contexts import MarshalFactoryContext
from ..api.contexts import UnmarshalFactoryContext
from ..api.types import Marshaler
from ..api.types import MarshalerFactory
from ..api.types import Unmarshaler
from ..api.types import UnmarshalerFactory
from ..api.vias import MarshalVia
from ..api.vias import UnmarshalVia
from ..api.vias import _MarshalViaMetadata
from ..api.vias import _UnmarshalViaMetadata
from ..api.vias import make_marshaler_via
from ..api.vias import make_unmarshaler_via


T = ta.TypeVar('T')


##


class ViaConfigMarshalerFactory(MarshalerFactory):
    def make_marshaler(self, ctx: MarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], Marshaler] | None:
        if (key := rty.runtime_object) is None:
            return None

        if (via := ctx.configs.get(key).get(MarshalVia)) is None:
            return None

        return lambda: make_marshaler_via(ctx, rty, via)


class ViaConfigUnmarshalerFactory(UnmarshalerFactory):
    def make_unmarshaler(self, ctx: UnmarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], Unmarshaler] | None:
        if (key := rty.runtime_object) is None:
            return None

        if (via := ctx.configs.get(key).get(UnmarshalVia)) is None:
            return None

        return lambda: make_unmarshaler_via(ctx, rty, via)


##


def _get_via_metadata(rty: rfl.Type, md_cls: type[T]) -> T | None:
    if (cls := rfl.get_runtime_type_or_none(rty)) is None:
        return None

    return md.get_single_object_metadata(cls, type=md_cls)


class ViaMetadataMarshalerFactory(MarshalerFactory):
    def make_marshaler(self, ctx: MarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], Marshaler] | None:
        if (vmd := _get_via_metadata(rty, _MarshalViaMetadata)) is None:
            return None

        return lambda: make_marshaler_via(ctx, rty, vmd.via)


class ViaMetadataUnmarshalerFactory(UnmarshalerFactory):
    def make_unmarshaler(self, ctx: UnmarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], Unmarshaler] | None:
        if (vmd := _get_via_metadata(rty, _UnmarshalViaMetadata)) is None:
            return None

        return lambda: make_unmarshaler_via(ctx, rty, vmd.via)
