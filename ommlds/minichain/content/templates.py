from omlish import lang
from omlish.text import templating as tpl

from .dynamic import DynamicContent


##


class TemplateContent(DynamicContent, lang.Final):
    t: tpl.Templater
