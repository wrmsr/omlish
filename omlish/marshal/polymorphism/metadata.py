"""
        lmf = LazyMarshalerFactory(lambda: _marshal.PolymorphismMarshalerFactory(
            polymorphism_from_subclasses(
                cls,
                naming=opts.naming,
                strip_suffix=opts.strip_suffix,
            ),
            opts.type_tagging,
        ))

        luf = LazyUnmarshalerFactory(lambda: _unmarshal.PolymorphismUnmarshalerFactory(
            polymorphism_from_subclasses(
                cls,
                naming=opts.naming,
                strip_suffix=opts.strip_suffix,
            ),
            opts.type_tagging,
        ))
"""
import threading
import typing as ta

from ... import check
from ... import lang
from ... import metadata as md
from ... import reflect as rfl
from ..api.contexts import MarshalFactoryContext
from ..api.contexts import UnmarshalFactoryContext
from ..api.types import Marshaler
from ..api.types import MarshalerFactory
from ..api.types import Unmarshaler
from ..api.types import UnmarshalerFactory
from ..api.naming import Naming
from ..api.vias import MarshalVia
from ..api.vias import _MarshalViaMetadata
from ..api.vias import UnmarshalVia
from ..api.vias import _UnmarshalViaMetadata
from ..factories.lazy import LazyMarshalerFactory
from ..factories.lazy import LazyUnmarshalerFactory
from .api import AUTO_STRIP_SUFFIX
from .api import PolymorphismOptions
from .api import TypeTagging
from .api import WrapperTypeTagging
from .api import polymorphism_from_subclasses
from .marshal import PolymorphismMarshalerFactory
from .unmarshal import PolymorphismUnmarshalerFactory
from .api import _PolymorphismMetadata
from .api import Polymorphism
from .api import Impls
from ..api.configs import ConfigRegistry


FactoryT = ta.TypeVar('FactoryT', bound=MarshalerFactory | UnmarshalerFactory)
FactoryContextT = ta.TypeVar('FactoryContextT', bound=MarshalFactoryContext | UnmarshalFactoryContext)


##


def _get_polymorphism_metadata(rty: rfl.Type) -> _PolymorphismMetadata | None:
    if not isinstance(rty, type):
        return None

    if not (mds := md.get_object_metadata(rty, type=_PolymorphismMetadata)):
        return None

    return mds[-1]


class PolymorphismMetadataCache:
    def __init__(self) -> None:
        super().__init__()

        self._lock = threading.Lock()

        # self._metadata_cache

    # def get_metadata(self, rty: rfl.Type) -> _PolymorphismMetadata | None:
    #     try:
    #         return

    class Lookup(ta.NamedTuple):
        poly: Polymorphism
        opts: PolymorphismOptions

    def lookup(self, cfgs: ConfigRegistry, rty: rfl.Type) -> Lookup | None:
        raise NotImplementedError


##


class _PolymorphismMetadataFactory(ta.Generic[FactoryContextT, FactoryT]):
    def __init__(self, cache: PolymorphismMetadataCache) -> None:
        super().__init__()

        self._cache = cache


class PolymorphismMetadataMarshalerFactory(
    _PolymorphismMetadataFactory[MarshalFactoryContext, MarshalerFactory],
    MarshalerFactory,
):
    def make_marshaler(self, ctx: MarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], Marshaler] | None:
        if (lu := self._cache.lookup(check.isinstance(ctx.configs, ConfigRegistry), rty)) is None:
            return None

        return PolymorphismMarshalerFactory(
            lu.poly,
            lu.opts.type_tagging,
        ).make_marshaler(ctx, rty)


class PolymorphismMetadataUnmarshalerFactory(
    _PolymorphismMetadataFactory[UnmarshalFactoryContext, UnmarshalerFactory],
    UnmarshalerFactory,
):
    def make_unmarshaler(self, ctx: UnmarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], Unmarshaler] | None:
        if (lu := self._cache.lookup(check.isinstance(ctx.configs, ConfigRegistry), rty)) is None:
            return None

        return PolymorphismUnmarshalerFactory(
            lu.poly,
            lu.opts.type_tagging,
        ).make_unmarshaler(ctx, rty)


##


def make_polymorphism_metadata_factories() -> tuple[
    PolymorphismMetadataMarshalerFactory,
    PolymorphismMetadataUnmarshalerFactory,
]:
    return (
        PolymorphismMetadataMarshalerFactory(cache := PolymorphismMetadataCache()),
        PolymorphismMetadataUnmarshalerFactory(cache),
    )
