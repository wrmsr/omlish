import typing as ta

from omlish import check
from omlish.text import templating as tpl

from ..content import Content
from ..metadata import with_content_original
from ..templates import TemplateContent
from ..text import TextContent
from .visitors import VisitorContentTransform


C = ta.TypeVar('C')


##


class TemplateContentMaterializer(VisitorContentTransform[C]):
    def __init__(
            self,
            templater_context: tpl.Templater.Context | None = None,
    ) -> None:
        super().__init__()

        self._templater_context = templater_context

    def visit_template_content(self, c: TemplateContent, ctx: C) -> Content:
        s = c.t.render(check.not_none(self._templater_context))
        return with_content_original(TextContent(s), original=c)
