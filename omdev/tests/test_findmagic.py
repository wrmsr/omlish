"""
TODO:
 - comment modes: #, //, /* */
 - syntax modes: json, py
"""
import dataclasses as dc
import functools
import typing as ta


MAGIC_KEY_PREFIX = '@omlish-'


@dc.dataclass(frozen=True)
class Magic:
    key: str
    file: str | None
    start_line: int
    end_line: int
    raw: str
    prepared: ta.Any  # ast.AST | json.Value


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
#     "bar": 2,
# }
}
"""


C_TEST_FILE = """
// @omlish-magic-test

// @omlish-magic-test "foo"
// @omlish-magic-test "bar"
abcd

efg
// @omlish-magic-test {
//     "foo": 1,
//     "bar": 2,
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
    "bar": 2,
} */
bar }

/* @omlish-magic-test {
    "foo": 1,
    "bar": 2,
}
*/
bar }
"""


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
            out.append(line[len(prefix) + len(magic_key) + 1:])
        elif line.rstrip().endswith(suffix):
            out.append(line.rstrip()[:-len(suffix)])
            break
        else:
            out.append(line)
    else:
        return None
    return out


MagicPreparer: ta.TypeAlias = ta.Callable[[str], ta.Any | None]


def py_magic_preparer(src: str) -> ta.Any | None:
    try:
        prepared = compile(src, '<magic>', 'eval')
    except SyntaxError:
        return None
    return prepared


def find_magic(
        lines: ta.Sequence[str],
        *,
        file: str | None = None,
        magic_key_prefix: str = MAGIC_KEY_PREFIX,
        line_prefix: str | None = None,
        block_prefix_suffix: tuple[str, str] | None = None,
        preparer: MagicPreparer = py_magic_preparer,
) -> list[Magic]:
    out: list[Magic] = []

    start = 0
    while start < len(lines):
        start_line = lines[start]

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

            block_src = ''.join(['(', *block_lines, ')'])
            if (prepared := preparer(block_src)) is None:
                end += 1
                continue

            magic = Magic(
                key=key,
                file=file,
                start_line=start + 1,
                end_line=end + 1,
                raw=block_src,
                prepared=prepared,
            )
            break

        if magic is None:
            raise Exception(f'Failed to find magic block terminator : {file=} {start=} {end=}')

        out.append(magic)
        start = end + 1

    return out


def test_multiline_magic():
    print()

    for test_file, kw in [
        (PY_TEST_FILE.replace('%', '@'), dict(line_prefix='# ')),
        (C_TEST_FILE, dict(line_prefix='// ', block_prefix_suffix=('/* ', '*/'))),
    ]:
        magics = find_magic(
            test_file.splitlines(keepends=True),
            **kw,
        )
        print(magics)
