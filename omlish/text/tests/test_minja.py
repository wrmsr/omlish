# ruff: noqa: UP006 UP007
# @omlish-lite
import typing as ta
import unittest

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
    def test_minja(self) -> None:
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
