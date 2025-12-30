from omlish import dataclasses as dc
from omlish import lang
from omlish.text import templating as tpl

from .dynamic import DynamicContent


##


@dc.dataclass(frozen=True)
class TemplateContent(DynamicContent, lang.Final):
    t: tpl.Templater
