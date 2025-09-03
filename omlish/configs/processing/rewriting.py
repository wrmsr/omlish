# ruff: noqa: UP006 UP007 UP045
# @omlish-lite
import collections.abc
import dataclasses as dc
import typing as ta

from ...lite.abstract import Abstract
from ...lite.check import check
from ...lite.types import BUILTIN_SCALAR_ITERABLE_TYPES


T = ta.TypeVar('T')
StrT = ta.TypeVar('StrT', bound=str)
MappingT = ta.TypeVar('MappingT', bound=ta.Mapping)
IterableT = ta.TypeVar('IterableT', bound=ta.Iterable)

ConfigRewriterItem = ta.Union[int, str, None]  # ta.TypeAlias
ConfigRewriterPath = ta.Tuple[ConfigRewriterItem, ...]  # ta.TypeAlias


##


class RawConfigMetadata:
    def __new__(cls, *args, **kwargs):  # noqa
        raise TypeError


class ConfigRewriter(Abstract):
    @dc.dataclass(frozen=True)
    class Context(ta.Generic[T]):
        obj: T

        parent: ta.Optional['ConfigRewriter.Context'] = None
        item: ConfigRewriterItem = None

        raw: bool = False

        def __post_init__(self) -> None:
            if self.parent is None:
                check.none(self.item)

        @property
        def path(self) -> ConfigRewriterPath:
            cur: ConfigRewriter.Context = self
            lst: ta.List[ConfigRewriterItem] = []
            while True:
                if cur.parent is None:
                    break
                lst.append(cur.item)
                cur = cur.parent
            return tuple(reversed(lst))

        def make_child(
                self,
                obj: ta.Any,
                item: ConfigRewriterItem,
                **kwargs: ta.Any,
        ) -> 'ConfigRewriter.Context':
            return dc.replace(
                self,
                obj=obj,
                parent=self,
                item=item,
                **kwargs,
            )

    def rewrite_none(self, ctx: Context[None]) -> ta.Any:
        return ctx.obj

    def rewrite_dataclass(self, ctx: Context[T]) -> T:
        kw = {}
        for f in dc.fields(ctx.obj):  # type: ignore
            fv = getattr(ctx.obj, f.name)
            nfv: ta.Any = self.rewrite(ctx.make_child(
                fv,
                f.name,
                raw=bool(not f.metadata.get(RawConfigMetadata)),
            ))
            if fv is not nfv:
                kw[f.name] = nfv
        if not kw:
            return ctx.obj
        return dc.replace(ctx.obj, **kw)  # type: ignore

    def rewrite_str(self, ctx: Context[StrT]) -> StrT:
        return ctx.obj

    def rewrite_builtin_scalar_iterable(self, ctx: Context[IterableT]) -> IterableT:
        return ctx.obj

    def rewrite_mapping(self, ctx: Context[MappingT]) -> MappingT:
        nm = []
        b = False
        for mk, mv in ctx.obj.items():
            nk: ta.Any = self.rewrite(ctx.make_child(mk, None))
            nv: ta.Any = self.rewrite(ctx.make_child(mv, nk))
            nm.append((nk, nv))
            b |= nk is not mk or nv is not mv
        if not b:
            return ctx.obj
        return type(ctx.obj)(nm)  # type: ignore

    def rewrite_iterable(self, ctx: Context[IterableT]) -> IterableT:
        nl = []
        b = False
        for i, le in enumerate(ctx.obj):
            ne: ta.Any = self.rewrite(ctx.make_child(le, i))
            nl.append(ne)
            b |= ne is not le
        if not b:
            return ctx.obj
        return type(ctx.obj)(nl)  # type: ignore

    def rewrite_other(self, ctx: Context[T]) -> T:
        return ctx.obj

    def rewrite(self, ctx: Context[T]) -> T:
        if ctx.obj is None:
            return self.rewrite_none(ctx)  # type: ignore

        elif dc.is_dataclass(ctx.obj):
            return self.rewrite_dataclass(ctx)

        elif isinstance(ctx.obj, str):
            return self.rewrite_str(ctx)  # type: ignore

        elif isinstance(ctx.obj, BUILTIN_SCALAR_ITERABLE_TYPES):
            return self.rewrite_builtin_scalar_iterable(ctx)  # type: ignore

        elif isinstance(ctx.obj, collections.abc.Mapping):
            return self.rewrite_mapping(ctx)  # type: ignore

        elif isinstance(ctx.obj, (collections.abc.Sequence, collections.abc.Set)):
            return self.rewrite_iterable(ctx)  # type: ignore

        else:
            return self.rewrite_other(ctx)

    def __call__(self, v: T) -> T:
        return self.rewrite(self.Context(obj=v))
