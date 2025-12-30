"""
TODO:
 - attribution
"""
from omlish import dataclasses as dc
from omlish import lang

from .content import Content
from .standard import StandardContent


##


@dc.dataclass(frozen=True)
class QuoteContent(StandardContent, lang.Final):
    body: Content
