"""
FIXME:
 - str / list special case
 - ... pil image to b64 lol
"""
import dataclasses as dc
import typing as ta

from omlish import lang
from omlish import marshal as msh
from omlish import matchfns as mfs
from omlish import reflect as rfl

from .content import Content
from .content import ExtendedContent


##


class MarshalContent(lang.NotInstantiable, lang.Final):
    pass


@dc.dataclass(frozen=True)
class _ContentMarshaler(msh.Marshaler):
    et: msh.Marshaler

    def marshal(self, ctx: msh.MarshalContext, o: ta.Any) -> msh.Value:
        raise NotImplementedError


class _ContentMarshalerFactory(msh.MarshalerFactoryMatchClass):
    @mfs.simple(lambda _, ctx, rty: rty is MarshalContent)
    def _build(self, ctx: msh.MarshalContext, rty: rfl.Type) -> msh.Marshaler:
        return _ContentMarshaler(ctx.make(ExtendedContent))


@dc.dataclass(frozen=True)
class _ContentUnmarshaler(msh.Unmarshaler):
    et: msh.Unmarshaler

    def unmarshal(self, ctx: msh.UnmarshalContext, v: msh.Value) -> ta.Any:
        raise NotImplementedError


class _ContentUnmarshalerFactory(msh.UnmarshalerFactoryMatchClass):
    @mfs.simple(lambda _, ctx, rty: rty is MarshalContent)
    def _build(self, ctx: msh.UnmarshalContext, rty: rfl.Type) -> msh.Unmarshaler:
        return _ContentUnmarshaler(ctx.make(ExtendedContent))


##


@lang.static_init
def _install_standard_marshalling() -> None:
    extended_content_poly = msh.polymorphism_from_subclasses(ExtendedContent, naming=msh.Naming.SNAKE)
    msh.STANDARD_MARSHALER_FACTORIES[0:0] = [
        msh.PolymorphismMarshalerFactory(extended_content_poly),
        _ContentMarshalerFactory(),
    ]
    msh.STANDARD_UNMARSHALER_FACTORIES[0:0] = [
        msh.PolymorphismUnmarshalerFactory(extended_content_poly),
        _ContentUnmarshalerFactory(),
    ]

    msh.GLOBAL_REGISTRY.register(Content, msh.ReflectOverride(MarshalContent))
