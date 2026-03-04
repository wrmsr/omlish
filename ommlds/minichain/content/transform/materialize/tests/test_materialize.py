import typing as ta

from omlish.text import templating as tpl

from ....content import Content
from ....namespaces import ContentNamespace
from ....namespaces import NamespaceContent
from ....placeholders import ContentPlaceholder
from ....placeholders import PlaceholderContent
from ....resources import resource_content
from ....templates import TemplateContent
from ...recursive import RecursiveContentTransform
from ...types import ContentTransform
from ..namespaces import NamespaceContentMaterializer
from ..placeholders import PlaceholderContentMaterializer
from ..placeholders import PlaceholderContents
from ..resources import ResourceContentMaterializer
from ..templates import TemplateContentMaterializer


C = ta.TypeVar('C')


##


class DefaultContentMaterializer(ContentTransform[C]):
    def __init__(
            self,
            *,
            placeholder_contents: PlaceholderContents | None = None,
            templater_context: tpl.Templater.Context | None = None,
    ) -> None:
        super().__init__()

        self._recursive_materializer = RecursiveContentTransform[C](
            NamespaceContentMaterializer[C](),
            PlaceholderContentMaterializer[C](placeholder_contents),
            ResourceContentMaterializer[C](),
        )

        self._template_materializer = TemplateContentMaterializer[C](templater_context)

    def transform(self, c: Content, ctx: C) -> Content:
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
    ).transform(c, None)


##


class BarContentPlaceholder(ContentPlaceholder):
    pass


def test_materialize():
    for c, kw in [
        ('hi', {}),
        (
            TemplateContent(tpl.format_templater('{hi}')),
            dict(templater_context=tpl.templater_context(dict(hi='yes'))),
        ),
        (
            [
                'abc',
                PlaceholderContent('foo'),
                'def',
            ],
            dict(placeholder_contents={'foo': 'bar'}),
        ),
        (
            [
                'abc',
                PlaceholderContent(BarContentPlaceholder),
                'def',
            ],
            dict(placeholder_contents={'foo': 'bar', BarContentPlaceholder: PlaceholderContent('foo')}),
        ),
        (
            resource_content(__package__, 'foo.md'),
            {},
        ),
    ]:
        print(c)
        nc = materialize_content(c, **kw)  # type: ignore
        print(nc)


def test_materialize_namespace():
    class FooContent(ContentNamespace):
        FOO = 'foo!'
        BAR = 'bar!'

    print(materialize_content(NamespaceContent(FooContent)))
