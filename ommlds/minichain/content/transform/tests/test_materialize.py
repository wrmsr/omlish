from omlish.text import templating as tpl

from ...namespaces import ContentNamespace
from ...namespaces import NamespaceContent
from ...placeholders import ContentPlaceholder
from ...placeholders import PlaceholderContent
from ...templates import TemplateContent
from ..materialize import materialize_content


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
    ]:
        print(c)
        nc = materialize_content(c, **kw)  # type: ignore
        print(nc)


def test_materialize_namespace():
    class FooContent(ContentNamespace):
        FOO = 'foo!'
        BAR = 'bar!'

    print(materialize_content(NamespaceContent(FooContent)))
