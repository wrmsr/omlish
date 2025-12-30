from omlish import dataclasses as dc
from omlish import lang
from omlish.text import templating as tpl

from .content import LeafContent
from .dynamic import DynamicContent


##


@dc.dataclass(frozen=True)
class TemplateContent(DynamicContent, LeafContent, lang.Final):
    t: tpl.Templater
