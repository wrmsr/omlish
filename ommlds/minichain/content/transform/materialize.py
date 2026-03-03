import abc
import typing as ta

from omlish import dataclasses as dc
from omlish import lang
from omlish.text import templating as tpl

from ..content import Content
from .namespaces import NamespaceContentMaterializer
from .placeholders import PlaceholderContentMaterializer
from .placeholders import PlaceholderContents
from .recursive import RecursiveContentMaterializer
from .resources import ResourceContentMaterializer
from .templates import TemplateContentMaterializer
from .types import ContentTransform


C = ta.TypeVar('C')


##


class ContentMaterializer(lang.Abstract, ta.Generic[C]):
    @abc.abstractmethod
    def materialize(self, c: Content, ctx: C) -> Content:
        raise NotImplementedError


##


@dc.dataclass(frozen=True)
class ContentMaterializerContentTransform(ContentTransform[C]):
    cm: ContentMaterializer[C]

    def transform(self, c: Content, ctx: C) -> Content:
        return self.cm.materialize(c, ctx)


##


class DefaultContentMaterializer(ContentMaterializer[C]):
    def __init__(
            self,
            *,
            placeholder_contents: PlaceholderContents | None = None,
            templater_context: tpl.Templater.Context | None = None,
    ) -> None:
        super().__init__()

        self._recursive_materializer = RecursiveContentMaterializer[C](
            NamespaceContentMaterializer[C](),
            PlaceholderContentMaterializer[C](placeholder_contents),
            ResourceContentMaterializer[C](),
        )

        self._template_materializer = TemplateContentMaterializer[C](templater_context)

    def materialize(self, c: Content, ctx: C) -> Content:
        c = self._recursive_materializer.transform(c, ctx)
        c = self._template_materializer.transform(c, ctx)
        return c


def materialize_content(
        c: Content,
        *,
        placeholder_contents: PlaceholderContents | None = None,
        templater_context: tpl.Templater.Context | None = None,
) -> Content:
    return DefaultContentMaterializer[None](
        placeholder_contents=placeholder_contents,
        templater_context=templater_context,
    ).materialize(c, None)
