from omlish import check
from omlish.text import templating as tpl

from ..templates import TemplateContent
from ..types import Content
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
        return c.t.render(check.not_none(self._templater_context))
