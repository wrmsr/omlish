"""
FIXME:
 - str / list special case
 - ... pil image to b64 lol
"""
import typing as ta

from omlish import lang
from omlish import marshal as msh
from omlish import matchfns as mfs
from omlish import reflect as rfl

from .content import Content
from .content import ExtendedContent


class _Content(lang.NotInstantiable, lang.Final):
    pass


class _ContentMarshaler(msh.Marshaler):
    def marshal(self, ctx: msh.MarshalContext, o: ta.Any) -> msh.Value:
        raise NotImplementedError


class _ContentMarshalerFactory(msh.MarshalerFactoryMatchClass):
    @mfs.simple(lambda _, ctx, rty: rty is _Content)
    def _build(self, ctx: msh.MarshalContext, rty: rfl.Type) -> msh.Marshaler:
        raise NotImplementedError


@lang.static_init
def _install_standard_marshalling() -> None:
    extended_content_poly = msh.polymorphism_from_subclasses(ExtendedContent, naming=msh.Naming.SNAKE)
    msh.STANDARD_MARSHALER_FACTORIES[0:0] = [
        msh.PolymorphismMarshalerFactory(extended_content_poly),
        _ContentMarshalerFactory(),
    ]
    msh.STANDARD_UNMARSHALER_FACTORIES[0:0] = [
        msh.PolymorphismUnmarshalerFactory(extended_content_poly),
    ]

    msh.GLOBAL_REGISTRY.register(Content, msh.ReflectOverride(_Content))
