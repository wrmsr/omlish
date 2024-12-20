import unittest

from ..find import compile_magic_style_pat
from ..find import find_magic
from ..magic import Magic
from ..prepare import json_magic_preparer
from ..prepare import py_eval_magic_preparer
from ..styles import C_MAGIC_STYLE
from ..styles import PY_MAGIC_STYLE


##


PY_TEST_FILE = """
# %omlish-magic-test

# %omlish-magic-test
"bar"

# %omlish-magic-test
bar

# %omlish-magic-test "foo"

# %omlish-magic-test "foo"
"bar"

efg
# %omlish-magic-test "foo"
bar

# %omlish-magic-2-test "foo"
"bar"

# %omlish-magic-test "foo"
# %omlish-magic-test "bar"

# %omlish-magic-test "foo", "bar"

# %omlish-magic-test {"foo": 1, "bar": 2}

# %omlish-magic-test {
#     "foo": 1,
#     "bar": 2
# }
}
"""

PY_EXPECTED_MAGICS = [
    Magic(
        key='@omlish-magic-test',
        file=None,
        start_line=2,
        end_line=2,
        body='',
        prepared=None,
    ),
    Magic(
        key='@omlish-magic-test',
        file=None,
        start_line=4,
        end_line=4,
        body='',
        prepared=None,
    ),
    Magic(
        key='@omlish-magic-test',
        file=None,
        start_line=7,
        end_line=7,
        body='',
        prepared=None,
    ),
    Magic(
        key='@omlish-magic-test',
        file=None,
        start_line=10,
        end_line=10,
        body='"foo"\n',
        prepared='foo',
    ),
    Magic(
        key='@omlish-magic-test',
        file=None,
        start_line=12,
        end_line=12,
        body='"foo"\n',
        prepared='foo',
    ),
    Magic(
        key='@omlish-magic-test',
        file=None,
        start_line=16,
        end_line=16,
        body='"foo"\n',
        prepared='foo',
    ),
    Magic(
        key='@omlish-magic-2-test',
        file=None,
        start_line=19,
        end_line=19,
        body='"foo"\n',
        prepared='foo',
    ),
    Magic(
        key='@omlish-magic-test',
        file=None,
        start_line=22,
        end_line=22,
        body='"foo"\n',
        prepared='foo',
    ),
    Magic(
        key='@omlish-magic-test',
        file=None,
        start_line=23,
        end_line=23,
        body='"bar"\n',
        prepared='bar',
    ),
    Magic(
        key='@omlish-magic-test',
        file=None,
        start_line=25,
        end_line=25,
        body='"foo", "bar"\n',
        prepared=('foo', 'bar'),
    ),
    Magic(
        key='@omlish-magic-test',
        file=None,
        start_line=27,
        end_line=27,
        body='{"foo": 1, "bar": 2}\n',
        prepared={'foo': 1, 'bar': 2},
    ),
    Magic(
        key='@omlish-magic-test',
        file=None,
        start_line=29,
        end_line=32,
        body='{\n    "foo": 1,\n    "bar": 2\n}\n',
        prepared={'foo': 1, 'bar': 2},
    ),
]


class TestPyFindMagic(unittest.TestCase):
    def test_py_find_magic(self):
        magics = find_magic(
            PY_MAGIC_STYLE,
            PY_TEST_FILE.replace('%', '@').splitlines(keepends=True),
            preparer=py_eval_magic_preparer,
        )

        assert magics == PY_EXPECTED_MAGICS


##


C_TEST_FILE = """
// @omlish-magic-test

// @omlish-magic-test "foo"
// @omlish-magic-test "bar"
abcd

efg
// @omlish-magic-test {
//     "foo": 1,
//     "bar": 2
// }
foo

/* @omlish-magic-test */

/* @omlish-magic-test "foo" */
/* @omlish-magic-test "foo"
*/

/* @omlish-magic-test "bar" */
bar */

/* @omlish-magic-test {
    "foo": 1,
    "bar": 2
} */
bar }

/* @omlish-magic-test {
    "foo": 1,
    "bar": 2
}
*/
bar }
"""

C_EXPECTED_MAGICS = [
    Magic(
        key='@omlish-magic-test',
        file=None,
        start_line=2,
        end_line=2,
        body='',
        prepared=None,
    ),
    Magic(
        key='@omlish-magic-test',
        file=None,
        start_line=4,
        end_line=4,
        body='"foo"\n',
        prepared='foo',
    ),
    Magic(
        key='@omlish-magic-test',
        file=None,
        start_line=5,
        end_line=5,
        body='"bar"\n',
        prepared='bar',
    ),
    Magic(
        key='@omlish-magic-test',
        file=None,
        start_line=9,
        end_line=12,
        body='{\n    "foo": 1,\n    "bar": 2\n}\n',
        prepared={'foo': 1, 'bar': 2},
    ),
    Magic(
        key='@omlish-magic-test',
        file=None,
        start_line=15,
        end_line=15,
        body='',
        prepared=None,
    ),
    Magic(
        key='@omlish-magic-test',
        file=None,
        start_line=17,
        end_line=17,
        body='"foo" ',
        prepared='foo',
    ),
    Magic(
        key='@omlish-magic-test',
        file=None,
        start_line=18,
        end_line=18,
        body='"foo"\n',
        prepared='foo',
    ),
    Magic(
        key='@omlish-magic-test',
        file=None,
        start_line=21,
        end_line=21,
        body='"bar" ',
        prepared='bar',
    ),
    Magic(
        key='@omlish-magic-test',
        file=None,
        start_line=24,
        end_line=27,
        body='{\n    "foo": 1,\n    "bar": 2\n} ',
        prepared={'foo': 1, 'bar': 2},
    ),
    Magic(
        key='@omlish-magic-test',
        file=None,
        start_line=30,
        end_line=33,
        body='{\n    "foo": 1,\n    "bar": 2\n}\n',
        prepared={'foo': 1, 'bar': 2},
    ),
]


class TestCFindMagic(unittest.TestCase):
    def test_c_find_magic(self):
        magics = find_magic(
            C_MAGIC_STYLE,
            C_TEST_FILE.splitlines(keepends=True),
            preparer=py_eval_magic_preparer,
        )

        assert magics == C_EXPECTED_MAGICS


##


PY_JSON_TEST_FILE = """
# %omlish-magic-test
bar

# %omlish-magic-test "foo"

# %omlish-magic-test "foo"
"bar"

efg
# %omlish-magic-test "foo"
bar

# %omlish-magic-test "foo"
# %omlish-magic-test "bar"

# %omlish-magic-test {"foo": 1, "bar": 2}

# %omlish-magic-test {
#     "foo": 1,
#     "bar": 2
# }
}
"""

PY_JSON_EXPECTED_MAGICS = [
    Magic(
        key='@omlish-magic-test',
        file=None,
        start_line=2,
        end_line=2,
        body='',
        prepared=None,
    ),
    Magic(
        key='@omlish-magic-test',
        file=None,
        start_line=5,
        end_line=5,
        body='"foo"\n',
        prepared='foo',
    ),
    Magic(
        key='@omlish-magic-test',
        file=None,
        start_line=7,
        end_line=7,
        body='"foo"\n',
        prepared='foo',
    ),
    Magic(
        key='@omlish-magic-test',
        file=None,
        start_line=11,
        end_line=11,
        body='"foo"\n',
        prepared='foo',
    ),
    Magic(
        key='@omlish-magic-test',
        file=None,
        start_line=14,
        end_line=14,
        body='"foo"\n',
        prepared='foo',
    ),
    Magic(
        key='@omlish-magic-test',
        file=None,
        start_line=15,
        end_line=15,
        body='"bar"\n',
        prepared='bar',
    ),
    Magic(
        key='@omlish-magic-test',
        file=None,
        start_line=17,
        end_line=17,
        body='{"foo": 1, "bar": 2}\n',
        prepared={'foo': 1, 'bar': 2},
    ),
    Magic(
        key='@omlish-magic-test',
        file=None,
        start_line=19,
        end_line=22,
        body='{\n    "foo": 1,\n    "bar": 2\n}\n',
        prepared={'foo': 1, 'bar': 2},
    ),
]


class TestJsonPyFindMagic(unittest.TestCase):
    def test_json_py_find_magic(self):
        magics = find_magic(
            PY_MAGIC_STYLE,
            PY_JSON_TEST_FILE.replace('%', '@').splitlines(keepends=True),
            preparer=json_magic_preparer,
        )

        assert magics == PY_JSON_EXPECTED_MAGICS


##


class TestMagicPats(unittest.TestCase):
    def test_py_pat(self):
        p = compile_magic_style_pat(PY_MAGIC_STYLE)

        assert p.match('# @omlish-foo')
        assert p.match('# @omlish-foo ')
        assert p.match('# @omlish-foo {')

        assert not p.match('@omlish-foo')
        assert not p.match('# @xmlish-foo')
        assert not p.match('# omlish-foo')

    def test_py_keys_pat(self):
        p = compile_magic_style_pat(PY_MAGIC_STYLE, keys=['@omlish-foo', '@omlish-bar'])

        assert p.match('# @omlish-foo')
        assert p.match('# @omlish-foo ')
        assert p.match('# @omlish-foo {')
        assert p.match('# @omlish-bar')

        assert not p.match('@omlish-foo')
        assert not p.match('# @xmlish-foo')
        assert not p.match('# omlish-foo')

        assert not p.match('@omlish-foo2')
        assert not p.match('# @xmlish-foo2')
        assert not p.match('# omlish-foo2')

    def test_c_pat(self):
        p = compile_magic_style_pat(C_MAGIC_STYLE)

        assert p.match('// @omlish-foo')
        assert p.match('// @omlish-foo ')
        assert p.match('// @omlish-foo {')

        assert not p.match('@omlish-foo')
        assert not p.match('// @xmlish-foo')
        assert not p.match('// omlish-foo')

        assert p.match('/* @omlish-foo')
        assert p.match('/* @omlish-foo ')
        assert p.match('/* @omlish-foo {')

        assert not p.match('@omlish-foo')
        assert not p.match('/* @xmlish-foo')
        assert not p.match('/* omlish-foo')
