import collections.abc
import dataclasses as dc
import typing as ta

from omlish import lang
from omlish import marshal as msh
from omlish import reflect as rfl
from omlish.funcs import match as mfs

from .content import Content
from .content import ExtendedContent
from .content import SingleContent
from .images import ImageContent  # noqa
from .list import ListContent  # noqa
from .text import TextContent  # noqa


##


# TODO: This hack should be obsolete with 3.14 / PEP 649, but reflect needs to grow recursive type support.
class MarshalContent(lang.NotInstantiable, lang.Final):
    pass


MarshalContentUnion: ta.TypeAlias = ta.Union[  # noqa
    ta.Sequence[MarshalContent],
    SingleContent,
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
            msh.Impl(ImageContent, 'image'),
            msh.Impl(ListContent, 'list'),
            msh.Impl(TextContent, 'text'),
        ],
    )

    msh.install_standard_factories(
        msh.PolymorphismMarshalerFactory(extended_content_poly),
        msh.TypeMapMarshalerFactory({ImageContent: _ImageContentMarshaler()}),
        _ContentMarshalerFactory(),
    )

    msh.install_standard_factories(
        msh.PolymorphismUnmarshalerFactory(extended_content_poly),
        msh.TypeMapUnmarshalerFactory({ImageContent: _ImageContentUnmarshaler()}),
        _ContentUnmarshalerFactory(),
    )

    msh.register_global(
        Content,
        msh.ReflectOverride(MarshalContent),
        identity=True,
    )
