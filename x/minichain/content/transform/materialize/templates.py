from omcore import check
from omcore.text import templating as tpl

from ...content import Content
from ...templates import TemplateContent
from ...text import TextContent
from ..visitors import VisitorContentTransform


##


class TemplateContentMaterializer(VisitorContentTransform):
    def __init__(
            self,
            templater_context: tpl.Templater.Context | None = None,
    ) -> None:
        super().__init__()

        self._templater_context = templater_context

    def visit_template_content(self, c: TemplateContent, ctx: None) -> Content:
        s = c.t.render(check.not_none(self._templater_context))
        return TextContent(s)
