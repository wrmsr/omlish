"""
TODO:
 - track BlockContent nesting depth?
 - section names? dedicated 'section' content with header and body?
"""
from omlish import dataclasses as dc
from omlish import lang

from .cancontent import CanContent
from .simple import SimpleExtendedContent


##


@dc.dataclass(frozen=True)
class TagContent(SimpleExtendedContent, lang.Final):
    tag: str
    body: CanContent
