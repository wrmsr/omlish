"""
TODO:
  - lazy load
  - serialize fs path not data
"""
import typing as ta

from omlish import dataclasses as dc
from omlish import lang
from omlish import marshal as msh

from .content import ExtendedContent


if ta.TYPE_CHECKING:
    import PIL.Image as pimg  # noqa
else:
    pimg = lang.proxy_import('PIL.Image')


##


class _ImageMarshaler(msh.Marshaler):
    def marshal(self, ctx: msh.MarshalContext, o: ta.Any) -> msh.Value:
        raise NotImplementedError


class _ImageUnmarshaler(msh.Unmarshaler):
    def unmarshal(self, ctx: msh.UnmarshalContext, v: msh.Value) -> ta.Any:
        raise NotImplementedError


##


@dc.dataclass(frozen=True)
@msh.update_fields_metadata(['i'], marshaler=_ImageMarshaler(), unmarshaler=_ImageUnmarshaler())
class Image(ExtendedContent, lang.Final):
    i: 'pimg.Image' = dc.field()
