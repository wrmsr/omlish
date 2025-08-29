import collections.abc
import dataclasses as dc
import typing as ta

from omlish import check
from omlish import lang
from omlish import marshal as msh
from omlish import reflect as rfl
from omlish.funcs import match as mfs

from .images import ImageContent  # noqa
from .materialize import CanContent
from .materialize import _InnerCanContent
from .sequence import BlockContent  # noqa
from .sequence import InlineContent  # noqa
from .text import TextContent  # noqa
from .types import CONTENT_RUNTIME_TYPES
from .types import Content
from .types import ExtendedContent


##


# TODO: This hack should be obsolete with 3.14 / PEP 649, but reflect needs to grow recursive type support.
class MarshalContent(lang.NotInstantiable, lang.Final):
    pass


MarshalContentUnion: ta.TypeAlias = ta.Union[  # noqa
    str,
    ExtendedContent,
    ta.Sequence[MarshalContent],
]


_MARSHAL_CONTENT_UNION_RTY = rfl.type_(MarshalContentUnion)


@dc.dataclass(frozen=True)
class _ContentMarshaler(msh.Marshaler):
    et: msh.Marshaler

    def marshal(self, ctx: msh.MarshalContext, o: ta.Any) -> msh.Value:
        if isinstance(o, str):
            return o
        elif isinstance(o, ta.Sequence):
            return [self.marshal(ctx, e) for e in o]
        elif isinstance(o, ExtendedContent):
            return self.et.marshal(ctx, o)
        else:
            raise TypeError(o)


class _ContentMarshalerFactory(msh.MarshalerFactoryMatchClass):
    @mfs.simple(lambda _, ctx, rty: rty is MarshalContent or rty == _MARSHAL_CONTENT_UNION_RTY)
    def _build(self, ctx: msh.MarshalContext, rty: rfl.Type) -> msh.Marshaler:
        return _ContentMarshaler(ctx.make(ExtendedContent))


@dc.dataclass(frozen=True)
class _ContentUnmarshaler(msh.Unmarshaler):
    et: msh.Unmarshaler

    def unmarshal(self, ctx: msh.UnmarshalContext, v: msh.Value) -> ta.Any:
        if isinstance(v, str):
            return v
        elif isinstance(v, ta.Sequence):
            return [self.unmarshal(ctx, e) for e in v]
        elif isinstance(v, collections.abc.Mapping):
            return self.et.unmarshal(ctx, v)  # noqa
        else:
            raise TypeError(v)


class _ContentUnmarshalerFactory(msh.UnmarshalerFactoryMatchClass):
    @mfs.simple(lambda _, ctx, rty: rty is MarshalContent or rty == _MARSHAL_CONTENT_UNION_RTY)
    def _build(self, ctx: msh.UnmarshalContext, rty: rfl.Type) -> msh.Unmarshaler:
        return _ContentUnmarshaler(ctx.make(ExtendedContent))


##


class MarshalCanContent(lang.NotInstantiable, lang.Final):
    pass


MarshalCanContentUnion: ta.TypeAlias = ta.Union[  # noqa
    ta.Iterable[MarshalCanContent],
    _InnerCanContent,
]


_MARSHAL_CAN_CONTENT_UNION_RTY = rfl.type_(MarshalCanContentUnion)


@dc.dataclass(frozen=True)
class _CanContentMarshaler(msh.Marshaler):
    c: msh.Marshaler

    def marshal(self, ctx: msh.MarshalContext, o: ta.Any) -> msh.Value:
        return self.c.marshal(ctx, check.isinstance(o, CONTENT_RUNTIME_TYPES))


class _CanContentMarshalerFactory(msh.MarshalerFactoryMatchClass):
    @mfs.simple(lambda _, ctx, rty: rty is MarshalCanContent or rty == _MARSHAL_CAN_CONTENT_UNION_RTY)
    def _build(self, ctx: msh.MarshalContext, rty: rfl.Type) -> msh.Marshaler:
        return _CanContentMarshaler(ctx.make(Content))


@dc.dataclass(frozen=True)
class _CanContentUnmarshaler(msh.Unmarshaler):
    c: msh.Unmarshaler

    def unmarshal(self, ctx: msh.UnmarshalContext, v: msh.Value) -> ta.Any:
        return self.c.unmarshal(ctx, v)


class _CanContentUnmarshalerFactory(msh.UnmarshalerFactoryMatchClass):
    @mfs.simple(lambda _, ctx, rty: rty is MarshalCanContent or rty == _MARSHAL_CAN_CONTENT_UNION_RTY)
    def _build(self, ctx: msh.UnmarshalContext, rty: rfl.Type) -> msh.Unmarshaler:
        return _CanContentUnmarshaler(ctx.make(Content))


##


class _ImageContentMarshaler(msh.Marshaler):
    def marshal(self, ctx: msh.MarshalContext, o: ta.Any) -> msh.Value:
        raise NotImplementedError


class _ImageContentUnmarshaler(msh.Unmarshaler):
    def unmarshal(self, ctx: msh.UnmarshalContext, v: msh.Value) -> ta.Any:
        raise NotImplementedError


##


@lang.static_init
def _install_standard_marshalling() -> None:
    extended_content_poly = msh.Polymorphism(
        ExtendedContent,
        [
            msh.Impl(InlineContent, 'inline'),
            msh.Impl(BlockContent, 'block'),
            msh.Impl(ImageContent, 'image'),
            msh.Impl(TextContent, 'text'),
        ],
    )

    msh.install_standard_factories(
        msh.PolymorphismMarshalerFactory(extended_content_poly),
        msh.TypeMapMarshalerFactory({ImageContent: _ImageContentMarshaler()}),
        _ContentMarshalerFactory(),
        _CanContentMarshalerFactory(),
    )

    msh.install_standard_factories(
        msh.PolymorphismUnmarshalerFactory(extended_content_poly),
        msh.TypeMapUnmarshalerFactory({ImageContent: _ImageContentUnmarshaler()}),
        _ContentUnmarshalerFactory(),
        _CanContentUnmarshalerFactory(),
    )

    msh.register_global_config(
        Content,
        msh.ReflectOverride(MarshalContent),
        identity=True,
    )

    msh.register_global_config(
        CanContent,
        msh.ReflectOverride(MarshalCanContent),
        identity=True,
    )
