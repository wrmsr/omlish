# ruff: noqa: UP006 UP007
import jinja2

from ..minja import render_minja_template


def test_minja() -> None:
    for tmpl, ctx in [
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

    ]:
        print('=== jinja ===')
        print(jinja2.Template(tmpl).render(**ctx))
        print('=== end jinja ===')
        print()

        print('=== minja ===')
        print(render_minja_template(tmpl, **ctx))
        print('=== end minja ===')
        print()
