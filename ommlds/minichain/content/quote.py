"""
TODO:
 - attribution
"""
from omlish import dataclasses as dc
from omlish import lang

from .standard import StandardContent
from .types import Content


##


@dc.dataclass(frozen=True)
class QuoteContent(StandardContent, lang.Final):
    body: Content
