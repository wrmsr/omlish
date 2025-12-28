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
    print(materialize_content('hi'))
    print(materialize_content(
        TemplateContent(tpl.format_templater('{hi}')),
        templater_context=tpl.templater_context(dict(hi='yes')),
    ))
    print(materialize_content([
        'abc',
        PlaceholderContent('foo'),
        'def',
    ], placeholder_contents={'foo': 'bar'}))
    print(materialize_content([
        'abc',
        PlaceholderContent(BarContentPlaceholder),
        'def',
    ], placeholder_contents={'foo': 'bar', BarContentPlaceholder: PlaceholderContent('foo')}))


def test_materialize_namespace():
    class FooContent(ContentNamespace):
        FOO = 'foo!'
        BAR = 'bar!'

    print(materialize_content(NamespaceContent(FooContent)))
