"""
TODO:
  - lazy load
  - serialize fs path not data
"""
import typing as ta

from omlish import dataclasses as dc
from omlish import lang

from .simple import SimpleSingleExtendedContent


if ta.TYPE_CHECKING:
    import PIL.Image as pimg  # noqa
else:
    pimg = lang.proxy_import('PIL.Image')


##


@dc.dataclass(frozen=True)
class ImageContent(SimpleSingleExtendedContent, lang.Final):
    i: 'pimg.Image' = dc.field()
