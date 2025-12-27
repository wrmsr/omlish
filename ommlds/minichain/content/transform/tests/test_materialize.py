from omlish.text import templating as tpl

from ..materialize import materialize_content
from ..namespaces import ContentNamespace
from ..placeholders import content_placeholder


def test_materialize():
    print(materialize_content('hi'))
    print(materialize_content(
        tpl.format_templater('{hi}'),
        templater_context=tpl.templater_context(dict(hi='yes')),
    ))
    print(materialize_content([
        'abc',
        (foo_cp := content_placeholder()),
        'def',
    ], content_placeholders={foo_cp: 'bar'}))
    print(materialize_content([
        'abc',
        (bar_cp := content_placeholder()),
        'def',
    ], content_placeholders={foo_cp: 'bar', bar_cp: foo_cp}))


def test_materialize_namespace():
    class FooContent(ContentNamespace):
        FOO = 'foo!'
        BAR = 'bar!'

    print(materialize_content(FooContent))
