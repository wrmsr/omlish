# ruff: noqa: PT009 PT027 UP006 UP007 UP045
# @omlish-lite
import operator
import typing as ta
import unittest

from ..minja import MinjaTemplateParam
from ..minja import compile_minja_template
from ..minja import render_minja_template


TEMPLATE_TEST_CASES = [
    (
        """\
Hello {{ name }}!
{# This is a comment and should not appear #}
{% for item in items %}
- {{ item.upper() }}
{% endfor %}
Some function call: {{ len(items) }} items total.
""",
        {
            'name': 'World',
            'items': ['apple', 'banana', 'cherry'],
            'len': len,
        },
    ),

    (
        """\
Hello {{ name }}!
{# This is a comment and should not appear #}
{% for item in items %}
- {{ item.upper() }}
{% if item == 'banana' %}
it's a banana!
{% elif item == 'cherry' %}
no it's a cherry!
{% else %}
it's something else!
{% endif %}
{% endfor %}
Some function call: {{ len(items) }} items total.
""",
        {
            'name': 'World',
            'items': ['apple', 'banana', 'cherry'],
            'len': len,
        },
    ),

    (
        """\
Hello {{ name }}!
{#- This is a comment and should not appear -#}
{% for item in items %}
- {{ item.upper() }}
{% if item == 'banana' %}
it's a banana!
{% elif item == 'cherry' %}
no it's a cherry!
{% else %}
it's something else!
{% endif %}
{% endfor %}
Some function call: {{ len(items) }} items total.
""",
        {
            'name': 'World',
            'items': ['apple', 'banana', 'cherry'],
            'len': len,
        },
    ),

]


class TestMinja(unittest.TestCase):
    def test_minja(self):
        jinja2: ta.Any
        try:
            import jinja2
        except ImportError:
            jinja2 = None

        for tmpl, ctx in TEMPLATE_TEST_CASES:
            if jinja2 is not None:
                print('=== jinja ===')
                print(jinja2.Template(tmpl).render(**ctx))
                print('=== end jinja ===')
                print()

            print('=== minja ===')
            print(render_minja_template(tmpl, **ctx))
            print('=== end minja ===')
            print()

    def test_helper(self):
        s = render_minja_template('{{ operator.add(x, 1) }}', operator=operator, x=1)
        self.assertEqual(s, '2')

    def test_stmts(self):
        s = render_minja_template(
            '\n'.join([
                '{%- y = x + 1 -%}',
                '{{ y }}',
            ]),
            x=1,
        )
        self.assertEqual(s, '2')

        s = render_minja_template(
            '\n'.join([
                '{%- y = {"foo", x, x} -%}',
                '{{ len(y) }}',
            ]),
            x=1,
        )
        self.assertEqual(s, '2')

    def test_strict_strings(self):
        self.assertEqual(compile_minja_template('{{ "hi" }}')(), 'hi')
        self.assertEqual(compile_minja_template('{{ 5 }}')(), '5')
        self.assertEqual(compile_minja_template('{{ "hi" }}', strict_strings=True)(), 'hi')
        with self.assertRaises(TypeError):
            compile_minja_template('{{ 5 }}', strict_strings=True)()

    def test_params(self):
        tmpl = compile_minja_template('foo {{ bar }}', ['bar'])
        self.assertEqual(tmpl(bar='hi'), 'foo hi')
        with self.assertRaises(TypeError):
            tmpl()

        tmpl = compile_minja_template(
            'foo {{ bar }}',
            [
                MinjaTemplateParam.new('bar', 420),
            ],
        )
        self.assertEqual(tmpl(), 'foo 420')
        self.assertEqual(tmpl(bar='hi'), 'foo hi')

        tmpl = compile_minja_template(
            'foo {{ bar }} {{ baz }}',
            [
                MinjaTemplateParam.new('bar', 420),
                MinjaTemplateParam.new('baz', 421),
            ],
        )
        self.assertEqual(tmpl(), 'foo 420 421')
        self.assertEqual(tmpl(bar='hi'), 'foo hi 421')
        self.assertEqual(tmpl(baz='bye'), 'foo 420 bye')
        self.assertEqual(tmpl(bar='hi', baz='bye'), 'foo hi bye')
