import threading
import typing as ta

from ... import metadata as md
from ... import reflect as rfl
from ..api.contexts import MarshalFactoryContext
from ..api.contexts import UnmarshalFactoryContext
from ..api.types import Marshaler
from ..api.types import MarshalerFactory
from ..api.types import Unmarshaler
from ..api.types import UnmarshalerFactory
from .api import Polymorphism
from .api import PolymorphismOptions
from .api import _PolymorphismMetadata
from .api import polymorphism_from_subclasses
from .marshal import PolymorphismMarshalerFactory
from .unmarshal import PolymorphismUnmarshalerFactory


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

        self._type_cache: dict[type, PolymorphismMetadataCache._TypeCacheEntry] = {}

    class _TypeCacheEntry(ta.NamedTuple):
        md: _PolymorphismMetadata
        poly: Polymorphism

    #

    def _make_poly(self, ty: type, pmd: _PolymorphismMetadata) -> Polymorphism:
        if pmd.mode == 'subclasses':
            return polymorphism_from_subclasses(
                ty,
                naming=pmd.opts.naming,
                strip_suffix=pmd.opts.strip_suffix,
            )

        else:
            raise RuntimeError(f'Unsupported polymorphism mode: {pmd.mode}')

    #

    class Lookup(ta.NamedTuple):
        poly: Polymorphism
        opts: PolymorphismOptions

    def _lookup_type(self, ty: type) -> Lookup | None:
        try:
            tce = self._type_cache[ty]
        except KeyError:
            pass
        else:
            return self.Lookup(tce.poly, tce.md.opts)

        if not md.has_object_metadata(ty):
            return None

        if (pmd := md.get_single_object_metadata(ty, type=_PolymorphismMetadata)) is None:
            return None

        with self._lock:
            try:
                tce = self._type_cache[ty]
            except KeyError:
                pass
            else:
                return self.Lookup(tce.poly, tce.md.opts)

            poly = self._make_poly(ty, pmd)

            self._type_cache[ty] = self._TypeCacheEntry(pmd, poly)

        return self.Lookup(poly, pmd.opts)

    def _lookup_union(self, rty: rfl.Union) -> Lookup | None:
        if not all(isinstance(a, type) for a in rty.args):
            return None

        if not (has_mds := [a for a in rty.args if md.has_object_metadata(a)]):  # noqa
            return None

        if not (pmd_tups := [  # noqa
            (a, pmd)
            for a in rty.args
            if (pmd := md.get_single_object_metadata(a, type=_PolymorphismMetadata)) is not None
        ]):
            return None

        if len(pmd_tups) != 1:
            return None

        [(pty, pmd)] = pmd_tups
        if not all(issubclass(a, pty) for a in rty.args):  # type: ignore
            return None

        raise NotImplementedError

    def lookup(self, rty: rfl.Type) -> Lookup | None:
        if isinstance(rty, type):
            return self._lookup_type(rty)
        elif isinstance(rty, rfl.Union):
            return self._lookup_union(rty)
        else:
            return None


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
        if (lu := self._cache.lookup(rty)) is None:
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
        if (lu := self._cache.lookup(rty)) is None:
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
