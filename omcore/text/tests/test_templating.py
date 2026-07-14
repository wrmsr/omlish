from ...testing import pytest as ptu
from ..templating import FormatTemplater
from ..templating import JinjaTemplater
from ..templating import MinjaTemplater
from ..templating import Pep292Templater
from ..templating import Templater


def test_templater():
    ctx = Templater.Context(env=dict(name='foo'))

    ft = FormatTemplater('Hi {name}')
    s = ft.render(ctx)
    assert s == 'Hi foo'

    pt = Pep292Templater.from_string('Hi ${name}')
    s = pt.render(ctx)
    assert s == 'Hi foo'

    mt = MinjaTemplater.from_string('Hi {{env["name"]}}')
    s = mt.render(ctx)
    assert s == 'Hi foo'


@ptu.skip.if_cant_import('jinja2')
def test_jinja2_templater():
    ctx = Templater.Context(env=dict(name='foo'))

    jt = JinjaTemplater.from_string('Hi {{name}}')
    s = jt.render(ctx)
    assert s == 'Hi foo'
