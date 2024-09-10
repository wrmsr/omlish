"""
TODO:
 - SandboxedEnvironment? worthless?
 - ugh, LINE NUMBERS
  - ** only track toplevel src line numbers **
  - SortedMapping[int, int] ? :/
 - also need to feed to serde
 - ugh, escape helper? {{ user.username|e }} - better if it’s not there?
 - lol, yaml jinja? :|
  - * line tracking there too lol *
 - extensions: jinja, j2
"""
import codecs
import linecache
import os
import re
import tempfile

import jinja2
import jinja2.nativetypes
import jinja2.nodes
import jinja2.parser
import jinja2.sandbox


SIMPLE_JINJA_PATTERN = re.compile(r'[A-Za-z_]+')


def is_simple_jinja(buf: str) -> bool:
    return SIMPLE_JINJA_PATTERN.fullmatch(buf) is not None


class StrictEnvironment(jinja2.Environment):

    def getitem(self, obj, argument):
        try:
            return obj[argument]
        except (AttributeError, TypeError, LookupError):
            return self.undefined(obj=obj, name=argument)

    def getattr(self, obj, attribute):
        try:
            return getattr(obj, attribute)
        except AttributeError:
            return self.undefined(obj=obj, name=attribute)


def test_simple_jinja():
    assert is_simple_jinja('x')
    assert not is_simple_jinja('x[0]')
    assert not is_simple_jinja('x | y')


def _linecache_inject(source, write):
    if write:
        tmp_file = tempfile.NamedTemporaryFile(
            prefix='iceworm-macro-',
            suffix='.py',
            delete=False,
            mode='w+',
            encoding='utf-8',
        )
        tmp_file.write(source)
        filename = tmp_file.name
    else:
        rnd = codecs.encode(os.urandom(12), 'hex')
        filename = rnd.decode('ascii')

    cache_entry = (
        len(source),
        None,
        [line + '\n' for line in source.splitlines()],
        filename,
    )
    linecache.cache[filename] = cache_entry
    return filename


class Parser(jinja2.parser.Parser):

    def parse_macro(self):
        node = jinja2.nodes.Macro(lineno=next(self.stream).lineno)
        node.name = self.parse_assign_target(name_only=True).name
        self.parse_signature(node)
        node.body = self.parse_statements(('name:endmacro',), drop_needle=True)
        return node


class Environment(jinja2.sandbox.SandboxedEnvironment):

    def _parse(self, source, name, filename):
        return Parser(self, source, name, filename).parse()

    def _compile(self, source, filename):
        if filename == '<template>':
            filename = _linecache_inject(source, True)
        return super()._compile(source, filename)


class NativeSandboxEnvironment(Environment):
    code_generator_class = jinja2.nativetypes.NativeCodeGenerator


TEXT_FILTERS = {
    'as_text': lambda x: x,
    'as_bool': lambda x: x,
    'as_native': lambda x: x,
    'as_number': lambda x: x,
}


def test_rendering():
    args = {
        'extensions': [
            'jinja2.ext.do',
            'jinja2.ext.loopcontrols',
        ],
    }

    env_cls = Environment
    filters = TEXT_FILTERS

    env = env_cls(**args)
    env.filters.update(filters)

    src = """
{%- macro hi(foo) -%}
    hi {{ foo -}}
    abcd
    bye {{ foo -}}
{% endmacro -%}

a
{{ hi(x) }}
b
{{ hi(y) }}
    """

    tmpl = env.from_string(src)

    print(tmpl.render())


def test_rewrap():
    class Undefined(jinja2.Undefined):
        def __str__(self):
            return '{{ ' + self._undefined_name + ' }}'
    env = jinja2.Environment(undefined=Undefined)
    tmpl = env.from_string('{{ a }} {{ b }} {{ "{{ barf(abc) }}" }} {{ c }}')
    assert tmpl.render({'a': 'A', 'c': 'C'}) == 'A {{ b }} {{ barf(abc) }} C'
