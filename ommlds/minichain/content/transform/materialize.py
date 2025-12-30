import abc

from omlish import lang
from omlish.text import templating as tpl

from ..content import Content
from .recursive import PlaceholderContents
from .recursive import RecursiveContentMaterializer
from .templates import TemplateContentMaterializer


##


class ContentMaterializer(lang.Abstract):
    @abc.abstractmethod
    def apply(self, c: Content) -> Content:
        raise NotImplementedError


##


class DefaultContentMaterializer(ContentMaterializer):
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
        c = RecursiveContentMaterializer(self._placeholder_contents).visit(c, None)
        c = TemplateContentMaterializer(self._templater_context).visit(c, None)
        return c


def materialize_content(
        c: Content,
        *,
        placeholder_contents: PlaceholderContents | None = None,
        templater_context: tpl.Templater.Context | None = None,
) -> Content:
    return DefaultContentMaterializer(
        placeholder_contents=placeholder_contents,
        templater_context=templater_context,
    ).apply(c)
