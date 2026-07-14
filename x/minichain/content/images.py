"""
TODO:
  - lazy load
  - serialize fs path not data
"""
import typing as ta

from omcore import dataclasses as dc
from omcore import lang

from .standard import StandardContent


if ta.TYPE_CHECKING:
    import PIL.Image as pimg  # noqa
else:
    pimg = lang.proxy_import('PIL.Image')


##


@dc.dataclass(frozen=True)
@dc.extra_class_params(terse_repr=True)
class ImageContent(StandardContent, lang.Final):
    i: pimg.Image = dc.field()
