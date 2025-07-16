from omlish.text import templating as tpl

from ..materialize import materialize_content
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
