from omlish import check
from omlish.text import templating as tpl

from ..content import Content
from ..metadata import ContentOriginal
from ..templates import TemplateContent
from ..text import TextContent
from .base import ContentTransform


##


class TemplateContentMaterializer(ContentTransform):
    def __init__(
            self,
            templater_context: tpl.Templater.Context | None = None,
    ) -> None:
        super().__init__()

        self._templater_context = templater_context

    @ContentTransform.apply.register
    def apply_template_content(self, c: TemplateContent) -> Content:
        s = c.t.render(check.not_none(self._templater_context))
        return TextContent(s).update_metadata(ContentOriginal(c))
