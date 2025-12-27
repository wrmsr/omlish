import collections.abc
import typing as ta

from omlish import check
from omlish import dataclasses as dc
from omlish import lang
from omlish import marshal as msh
from omlish import reflect as rfl

from .code import CodeContent  # noqa
from .dynamic import DynamicContent  # noqa
from .images import ImageContent  # noqa
from .json import JsonContent  # noqa
from .quote import QuoteContent  # noqa
from .raw import NON_STR_SINGLE_RAW_CONTENT_TYPES
from .raw import NonStrSingleRawContent
from .raw import RawContent  # noqa
from .raw import SingleRawContent  # noqa
from .section import SectionContent  # noqa
from .sequence import BlockContent  # noqa
from .sequence import InlineContent  # noqa
from .sequence import ItemListContent  # noqa
from .tag import TagContent  # noqa
from .text import TextContent  # noqa
from .types import CONTENT_TYPES  # noqa
from .types import BaseContent
from .types import Content


##


# TODO: This hack should be obsolete with 3.14 / PEP 649, but reflect needs to grow recursive type support.
class MarshalContent(lang.NotInstantiable, lang.Final):
    pass


MarshalContentUnion: ta.TypeAlias = ta.Union[  # noqa
    str,
    BaseContent,
    ta.Sequence[MarshalContent],
]


_MARSHAL_CONTENT_UNION_RTY = rfl.type_(MarshalContentUnion)


@dc.dataclass(frozen=True)
class _ContentMarshaler(msh.Marshaler):
    bt: msh.Marshaler

    def marshal(self, ctx: msh.MarshalContext, o: ta.Any) -> msh.Value:
        if isinstance(o, str):
            return o
        elif isinstance(o, ta.Sequence):
            return [self.marshal(ctx, e) for e in o]
        elif isinstance(o, BaseContent):
            return self.bt.marshal(ctx, o)
        else:
            raise TypeError(o)


class _ContentMarshalerFactory(msh.MarshalerFactory):
    def make_marshaler(self, ctx: msh.MarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], msh.Marshaler] | None:
        if not (rty is MarshalContent or rty == _MARSHAL_CONTENT_UNION_RTY):
            return None
        return lambda: _ContentMarshaler(ctx.make_marshaler(BaseContent))


@dc.dataclass(frozen=True)
class _ContentUnmarshaler(msh.Unmarshaler):
    bt: msh.Unmarshaler

    def unmarshal(self, ctx: msh.UnmarshalContext, v: msh.Value) -> ta.Any:
        if isinstance(v, str):
            return v
        elif isinstance(v, ta.Sequence):
            return [self.unmarshal(ctx, e) for e in v]
        elif isinstance(v, collections.abc.Mapping):
            return self.bt.unmarshal(ctx, v)  # noqa
        else:
            raise TypeError(v)


class _ContentUnmarshalerFactory(msh.UnmarshalerFactory):
    def make_unmarshaler(self, ctx: msh.UnmarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], msh.Unmarshaler] | None:  # noqa
        if not (rty is MarshalContent or rty == _MARSHAL_CONTENT_UNION_RTY):
            return None
        return lambda: _ContentUnmarshaler(ctx.make_unmarshaler(BaseContent))


##


class MarshalSingleRawContent(lang.NotInstantiable, lang.Final):
    pass


_SINGLE_RAW_CONTENT_UNION_RTY = rfl.type_(SingleRawContent)


@dc.dataclass(frozen=True)
class _SingleRawContentMarshaler(msh.Marshaler):
    nst: msh.Marshaler

    def marshal(self, ctx: msh.MarshalContext, o: ta.Any) -> msh.Value:
        if isinstance(o, str):
            return o
        elif isinstance(o, NON_STR_SINGLE_RAW_CONTENT_TYPES):
            return self.nst.marshal(ctx, o)
        else:
            raise TypeError(o)


class _SingleRawContentMarshalerFactory(msh.MarshalerFactory):
    def make_marshaler(self, ctx: msh.MarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], msh.Marshaler] | None:
        if not (rty is MarshalSingleRawContent or rty == _SINGLE_RAW_CONTENT_UNION_RTY):
            return None
        return lambda: _SingleRawContentMarshaler(ctx.make_marshaler(NonStrSingleRawContent))


@dc.dataclass(frozen=True)
class _SingleRawContentUnmarshaler(msh.Unmarshaler):
    nst: msh.Unmarshaler

    def unmarshal(self, ctx: msh.UnmarshalContext, v: msh.Value) -> ta.Any:
        if isinstance(v, str):
            return v
        elif isinstance(v, collections.abc.Mapping):
            return self.nst.unmarshal(ctx, v)  # noqa
        else:
            raise TypeError(v)


class _SingleRawContentUnmarshalerFactory(msh.UnmarshalerFactory):
    def make_unmarshaler(self, ctx: msh.UnmarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], msh.Unmarshaler] | None:  # noqa
        if not (rty is MarshalSingleRawContent or rty == _SINGLE_RAW_CONTENT_UNION_RTY):
            return None
        return lambda: _SingleRawContentUnmarshaler(ctx.make_unmarshaler(NonStrSingleRawContent))


##


class MarshalRawContent(lang.NotInstantiable, lang.Final):
    pass


MarshalRawContentUnion: ta.TypeAlias = ta.Union[  # noqa
    SingleRawContent,
    ta.Sequence[MarshalRawContent],
]


_MARSHAL_RAW_CONTENT_UNION_RTY = rfl.type_(MarshalRawContentUnion)


@dc.dataclass(frozen=True)
class _RawContentMarshaler(msh.Marshaler):
    nst: msh.Marshaler

    def marshal(self, ctx: msh.MarshalContext, o: ta.Any) -> msh.Value:
        if isinstance(o, str):
            return o
        elif isinstance(o, ta.Sequence):
            return [self.marshal(ctx, e) for e in o]
        elif isinstance(o, NON_STR_SINGLE_RAW_CONTENT_TYPES):
            return self.nst.marshal(ctx, o)
        else:
            raise TypeError(o)


class _RawContentMarshalerFactory(msh.MarshalerFactory):
    def make_marshaler(self, ctx: msh.MarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], msh.Marshaler] | None:
        if not (rty is MarshalRawContent or rty == _MARSHAL_RAW_CONTENT_UNION_RTY):
            return None
        return lambda: _RawContentMarshaler(ctx.make_marshaler(NonStrSingleRawContent))


@dc.dataclass(frozen=True)
class _RawContentUnmarshaler(msh.Unmarshaler):
    nst: msh.Unmarshaler

    def unmarshal(self, ctx: msh.UnmarshalContext, v: msh.Value) -> ta.Any:
        if isinstance(v, str):
            return v
        elif isinstance(v, ta.Sequence):
            return [self.unmarshal(ctx, e) for e in v]
        elif isinstance(v, collections.abc.Mapping):
            return self.nst.unmarshal(ctx, v)  # noqa
        else:
            raise TypeError(v)


class _RawContentUnmarshalerFactory(msh.UnmarshalerFactory):
    def make_unmarshaler(self, ctx: msh.UnmarshalFactoryContext, rty: rfl.Type) -> ta.Callable[[], msh.Unmarshaler] | None:  # noqa
        if not (rty is MarshalRawContent or rty == _MARSHAL_RAW_CONTENT_UNION_RTY):
            return None
        return lambda: _RawContentUnmarshaler(ctx.make_unmarshaler(NonStrSingleRawContent))


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
    base_content_poly = msh.Polymorphism(
        BaseContent,
        [

            msh.Impl(CodeContent, 'code'),

            msh.Impl(ImageContent, 'image'),

            msh.Impl(JsonContent, 'json'),

            msh.Impl(QuoteContent, 'quote'),

            msh.Impl(SectionContent, 'section'),

            msh.Impl(BlockContent, 'block'),
            msh.Impl(InlineContent, 'inline'),
            msh.Impl(ItemListContent, 'item_list'),

            msh.Impl(TagContent, 'tag'),

            msh.Impl(TextContent, 'text'),

        ],
    )

    msh.install_standard_factories(
        *msh.standard_polymorphism_factories(
            base_content_poly,
            unions='partial',
        ),
    )

    #

    msh.install_standard_factories(
        _ContentMarshalerFactory(),
        _ContentUnmarshalerFactory(),
    )

    msh.register_global_config(
        Content,
        msh.ReflectOverride(MarshalContent),
        identity=True,
    )

    #

    msh.install_standard_factories(
        _SingleRawContentMarshalerFactory(),
        _SingleRawContentUnmarshalerFactory(),
    )

    msh.register_global_config(
        SingleRawContent,
        msh.ReflectOverride(MarshalSingleRawContent),
        identity=True,
    )

    #

    msh.install_standard_factories(
        _RawContentMarshalerFactory(),
        _RawContentUnmarshalerFactory(),
    )

    msh.register_global_config(
        RawContent,
        msh.ReflectOverride(MarshalRawContent),
        identity=True,
    )

    #

    msh.install_standard_factories(
        msh.TypeMapMarshalerFactory({
            ImageContent: _ImageContentMarshaler(),
            JsonContent: _JsonContentMarshaler(),
        }),
        msh.TypeMapUnmarshalerFactory({
            ImageContent: _ImageContentUnmarshaler(),
            JsonContent: _JsonContentUnmarshaler(),
        }),
    )
