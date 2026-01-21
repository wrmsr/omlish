import abc

from omlish import lang
from omlish.text import templating as tpl

from ..content import Content
from .namespaces import NamespaceContentMaterializer
from .placeholders import PlaceholderContentMaterializer
from .placeholders import PlaceholderContents
from .recursive import RecursiveContentMaterializer
from .resources import ResourceContentMaterializer
from .templates import TemplateContentMaterializer


##


class ContentMaterializer(lang.Abstract):
    @abc.abstractmethod
    def materialize(self, c: Content) -> Content:
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

        self._recursive_materializer = RecursiveContentMaterializer(
            NamespaceContentMaterializer(),
            PlaceholderContentMaterializer(placeholder_contents),
            ResourceContentMaterializer(),
        )

        self._template_materializer = TemplateContentMaterializer(templater_context)

    def materialize(self, c: Content) -> Content:
        c = self._recursive_materializer.transform(c, None)
        c = self._template_materializer.transform(c, None)
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
    ).materialize(c)
