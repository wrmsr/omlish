import collections.abc
import dataclasses as dc
import typing as ta

from omlish import check
from omlish import lang
from omlish import marshal as msh
from omlish import reflect as rfl

from .images import ImageContent  # noqa
from .json import JsonContent  # noqa
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


class _ContentMarshalerFactory(msh.MarshalerFactory):
    def make_marshaler(self, ctx: msh.MarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], msh.Marshaler] | None:
        if not (rty is MarshalContent or rty == _MARSHAL_CONTENT_UNION_RTY):
            return None
        return lambda: _ContentMarshaler(ctx.make_marshaler(ExtendedContent))


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


class _ContentUnmarshalerFactory(msh.UnmarshalerFactory):
    def make_unmarshaler(self, ctx: msh.UnmarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], msh.Unmarshaler] | None:  # noqa
        if not (rty is MarshalContent or rty == _MARSHAL_CONTENT_UNION_RTY):
            return None
        return lambda: _ContentUnmarshaler(ctx.make_unmarshaler(ExtendedContent))


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


class _CanContentMarshalerFactory(msh.MarshalerFactory):
    def make_marshaler(self, ctx: msh.MarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], msh.Marshaler] | None:
        if not (rty is MarshalCanContent or rty == _MARSHAL_CAN_CONTENT_UNION_RTY):
            return None
        return lambda: _CanContentMarshaler(ctx.make_marshaler(Content))


@dc.dataclass(frozen=True)
class _CanContentUnmarshaler(msh.Unmarshaler):
    c: msh.Unmarshaler

    def unmarshal(self, ctx: msh.UnmarshalContext, v: msh.Value) -> ta.Any:
        return self.c.unmarshal(ctx, v)


class _CanContentUnmarshalerFactory(msh.UnmarshalerFactory):
    def make_unmarshaler(self, ctx: msh.UnmarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], msh.Unmarshaler] | None:  # noqa
        if not (rty is MarshalCanContent or rty == _MARSHAL_CAN_CONTENT_UNION_RTY):
            return None
        return lambda: _CanContentUnmarshaler(ctx.make_unmarshaler(Content))


##


class _ImageContentMarshaler(msh.Marshaler):
    def marshal(self, ctx: msh.MarshalContext, o: ta.Any) -> msh.Value:
        raise NotImplementedError


class _ImageContentUnmarshaler(msh.Unmarshaler):
    def unmarshal(self, ctx: msh.UnmarshalContext, v: msh.Value) -> ta.Any:
        raise NotImplementedError


##


class _JsonContentMarshaler(msh.Marshaler):
    def marshal(self, ctx: msh.MarshalContext, o: ta.Any) -> msh.Value:
        return ta.cast(msh.Value, check.isinstance(o, JsonContent).v)


class _JsonContentUnmarshaler(msh.Unmarshaler):
    def unmarshal(self, ctx: msh.UnmarshalContext, v: msh.Value) -> ta.Any:
        return JsonContent(v)


##


@lang.static_init
def _install_standard_marshaling() -> None:
    extended_content_poly = msh.Polymorphism(
        ExtendedContent,
        [
            msh.Impl(InlineContent, 'inline'),
            msh.Impl(BlockContent, 'block'),
            msh.Impl(ImageContent, 'image'),
            msh.Impl(JsonContent, 'json'),
            msh.Impl(TextContent, 'text'),
        ],
    )

    msh.install_standard_factories(
        msh.PolymorphismMarshalerFactory(extended_content_poly),
        msh.TypeMapMarshalerFactory({
            ImageContent: _ImageContentMarshaler(),
            JsonContent: _JsonContentMarshaler(),
        }),
        _ContentMarshalerFactory(),
        _CanContentMarshalerFactory(),
    )

    msh.install_standard_factories(
        msh.PolymorphismUnmarshalerFactory(extended_content_poly),
        msh.TypeMapUnmarshalerFactory({
            ImageContent: _ImageContentUnmarshaler(),
            JsonContent: _JsonContentUnmarshaler(),
        }),
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
