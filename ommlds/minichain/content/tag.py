"""
TODO:
 - track BlockContent nesting depth?
 - section names? dedicated 'section' content with header and body?
"""
from omlish import dataclasses as dc
from omlish import lang

from .content import Content
from .standard import StandardContent


##


@dc.dataclass(frozen=True)
class TagContent(StandardContent, lang.Final):
    tag: str
    body: Content
