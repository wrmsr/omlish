from omlish.text import templating as tpl

from ..materialize import materialize_content


def test_materialize():
    print(materialize_content('hi'))
    print(materialize_content(
        tpl.format_templater('{hi}'),
        templater_context=tpl.templater_context(dict(hi='yes')),
    ))
