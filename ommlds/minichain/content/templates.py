from omlish import dataclasses as dc
from omlish import lang
from omlish.text import templating as tpl

from .dynamic import DynamicContent
from .types import LeafContent


##


@dc.dataclass(frozen=True)
class TemplateContent(DynamicContent, LeafContent, lang.Final):
    t: tpl.Templater
