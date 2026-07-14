from omcore import dataclasses as dc
from omcore import lang
from omcore.text import templating as tpl

from .dynamic import DynamicContent


##


@dc.dataclass(frozen=True)
@dc.extra_class_params(terse_repr=True)
class TemplateContent(DynamicContent, lang.Final):
    t: tpl.Templater
