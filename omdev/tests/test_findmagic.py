"""
TODO:
 - comment modes: #, //, /* */
 - syntax modes: json, py
"""
import dataclasses as dc
import functools
import json
import typing as ta


MAGIC_KEY_PREFIX = '@omlish-'


@dc.dataclass(frozen=True)
class Magic:
    key: str
    file: str | None
    start_line: int
    end_line: int
    body: str
    prepared: ta.Any  # ast.AST | json.Value


def chop_magic_lines(
        magic_key: str,
        prefix: str,
        lines: ta.Iterable[str],
) -> list[str] | None:
    out: list[str] = []
    for i, line in enumerate(lines):
        if not i:
            if not line.startswith(prefix + magic_key):
                return None
            out.append(line[len(prefix) + len(magic_key) + 1:])
        else:
            if not line.startswith(prefix):
                return None
            out.append(line[len(prefix):])
    return out


def chop_magic_block(
        magic_key: str,
        prefix: str,
        suffix: str,
        lines: ta.Iterable[str],
) -> list[str] | None:
    out: list[str] = []
    for i, line in enumerate(lines):
        if not i:
            if not line.startswith(prefix + magic_key):
                return None
            s = line[len(prefix) + len(magic_key) + 1:]
            if s.rstrip().endswith(suffix):
                out.append(s.rstrip()[:-len(suffix)])
                break
            out.append(s)
        elif line.rstrip().endswith(suffix):
            out.append(line.rstrip()[:-len(suffix)])
            break
        else:
            out.append(line)
    return out


MagicPreparer: ta.TypeAlias = ta.Callable[[str], ta.Any]


class MagicPrepareError(Exception):
    pass


def py_compile_magic_preparer(src: str) -> ta.Any:
    try:
        prepared = compile(f'({src})', '<magic>', 'eval')
    except SyntaxError:
        raise MagicPrepareError
    return prepared


def py_eval_magic_preparer(src: str) -> ta.Any:
    code = py_compile_magic_preparer(src)
    return eval(code)  # noqa


def json_magic_preparer(src: str) -> ta.Any:
    try:
        prepared = json.loads()
    except json.JSONDecodeError:
        raise MagicPrepareError
    return prepared


def find_magic(
        lines: ta.Sequence[str],
        *,
        file: str | None = None,
        magic_key_prefix: str = MAGIC_KEY_PREFIX,
        line_prefix: str | None = None,
        block_prefix_suffix: tuple[str, str] | None = None,
        preparer: MagicPreparer = py_compile_magic_preparer,
) -> list[Magic]:
    out: list[Magic] = []

    start = 0
    while start < len(lines):
        start_line = lines[start]

        chopper: ta.Callable[[ta.Iterable[str]], list[str] | None]
        if (
                line_prefix is not None and
                start_line.startswith(line_prefix + magic_key_prefix)
        ):
            key = start_line[len(line_prefix):].split()[0]
            chopper = functools.partial(
                chop_magic_lines,
                key,
                line_prefix,
            )

        elif (
                block_prefix_suffix is not None and
                start_line.startswith(block_prefix_suffix[0] + magic_key_prefix)
        ):
            key = start_line[len(block_prefix_suffix[0]):].split()[0]
            chopper = functools.partial(
                chop_magic_block,
                key,
                *block_prefix_suffix,
            )

        else:
            start += 1
            continue

        end = start
        magic: Magic | None = None
        while end < len(lines):
            block_lines = chopper(lines[start:end + 1])
            if block_lines is None:
                raise Exception(f'Failed to find magic block terminator : {file=} {start=} {end=}')

            block_src = ''.join(block_lines)
            if not block_src:
                prepared = None
            else:
                try:
                    prepared = preparer(block_src)
                except MagicPrepareError:
                    end += 1
                    continue

            magic = Magic(
                key=key,
                file=file,
                start_line=start + 1,
                end_line=end + 1,
                body=block_src,
                prepared=prepared,
            )
            break

        if magic is None:
            raise Exception(f'Failed to find magic block terminator : {file=} {start=} {end=}')

        out.append(magic)
        start = end + 1

    return out

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


def test_multiline_magic():
    for test_file, expected_magics, kw in [
        (
                PY_TEST_FILE.replace('%', '@'),
                PY_EXPECTED_MAGICS,
                dict(line_prefix='# '),
        ),
        (
                C_TEST_FILE,
                C_EXPECTED_MAGICS,
                dict(line_prefix='// ', block_prefix_suffix=('/* ', '*/')),
        ),
    ]:
        magics = find_magic(
            test_file.splitlines(keepends=True),
            preparer=py_eval_magic_preparer,
            **kw,
        )

        assert magics == expected_magics
