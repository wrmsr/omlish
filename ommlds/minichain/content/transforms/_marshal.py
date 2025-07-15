import dataclasses as dc
import typing as ta

from omlish import check
from omlish import lang
from omlish import marshal as msh
from omlish import reflect as rfl
from omlish.funcs import match as mfs
from omlish.text import templating as tpl

from ..types import CONTENT_RUNTIME_TYPES
from ..types import Content
from ..types import ExtendedContent
from .materialize import CanContent
from .materialize import ContentNamespace


##


# TODO: This hack should be obsolete with 3.14 / PEP 649, but reflect needs to grow recursive type support.
class MarshalCanContent(lang.NotInstantiable, lang.Final):
    pass


MarshalCanContentUnion: ta.TypeAlias = ta.Union[  # noqa
    str,
    ExtendedContent,
    ta.Iterable[MarshalCanContent],
    type[ContentNamespace],
    tpl.Templater,
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


@lang.static_init
def _install_standard_marshalling() -> None:
    msh.install_standard_factories(
        _CanContentMarshalerFactory(),
        _CanContentUnmarshalerFactory(),
    )

    msh.register_global(
        CanContent,
        msh.ReflectOverride(MarshalCanContent),
        identity=True,
    )
