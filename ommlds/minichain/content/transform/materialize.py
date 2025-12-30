import abc

from omlish import lang
from omlish.text import templating as tpl

from ..types import Content
from .placeholders import PlaceholderContentMaterializer
from .placeholders import PlaceholderContents
from .templates import TemplateContentMaterializer


##


class ContentMaterializer(lang.Abstract):
    @abc.abstractmethod
    def apply(self, c: Content) -> Content:
        raise NotImplementedError


##


class StandardContentMaterializer(ContentMaterializer):
    def __init__(
            self,
            *,
            placeholder_contents: PlaceholderContents | None = None,
            templater_context: tpl.Templater.Context | None = None,
    ) -> None:
        super().__init__()

        self._placeholder_contents = placeholder_contents
        self._templater_context = templater_context

    def apply(self, c: Content) -> Content:
        c = PlaceholderContentMaterializer(self._placeholder_contents).apply(c)
        c = TemplateContentMaterializer(self._templater_context).apply(c)
        return c


def materialize_content(
        c: Content,
        *,
        placeholder_contents: PlaceholderContents | None = None,
        templater_context: tpl.Templater.Context | None = None,
) -> Content:
    return StandardContentMaterializer(
        placeholder_contents=placeholder_contents,
        templater_context=templater_context,
    ).apply(c)
