import typing as ta

from omlish import dataclasses as dc
from omlish import lang

from .content import Content


if ta.TYPE_CHECKING:
    import PIL.Image as pimg  # noqa
else:
    pimg = lang.proxy_import('PIL.Image')


@dc.dataclass(frozen=True)
class Image(Content, lang.Final):
    i: 'pimg.Image'
