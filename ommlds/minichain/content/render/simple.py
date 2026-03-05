"""
RecursiveContentMaterializer[C](
    NamespaceContentMaterializer[C](),
    PlaceholderContentMaterializer[C](placeholder_contents),
    ResourceContentMaterializer[C](),
)
TemplateContentMaterializer[C](templater_context)
"""
from omlish import check

from ..content import Content
from .types import ContentStrRenderer


##


class SimpleContentStrRenderer(ContentStrRenderer):
    def render(self, c: Content) -> str:
        return check.isinstance(c, str)  # lol


##


def render_content_str(c: Content) -> str:
    return SimpleContentStrRenderer().render(c)
