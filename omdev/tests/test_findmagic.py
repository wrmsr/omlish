"""
TODO:
 - comment modes: #, //, /* */
 - syntax modes: json, py
"""
import dataclasses as dc
import typing as ta


MAGIC_KEY_PREFIX = '@omlish-'


@dc.dataclass(frozen=True)
class Magic:
    key: str
    file: str
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

# %omlish-magic-test "foo"
bar

# %omlish-magic-2-test "foo"
"bar"

# %omlish-magic-test "foo"
# %omlish-magic-test "bar"

# %omlish-magic-test "foo", "bar"

# %omlish-magic-test {"foo": 1, "bar": 2}

# %omlish-magic-test {
#     "foo": 1,',
#     "bar": 2',
# }
}
"""


TEST_MAGIC = '@omlish-magic-test'

PY_TESTS = [
    '@omlish-magic-test',
    '\n'.join([
        '@omlish-magic-test',
        '"bar"',
    ]),
    '\n'.join([
        '@omlish-magic-test',
        'bar',
    ]),

    '@omlish-magic-test "foo"',
    '\n'.join([
        '@omlish-magic-test "foo"',
        '"bar"',
    ]),
    '\n'.join([
        '@omlish-magic-test "foo"',
        'bar',
    ]),

    '\n'.join([
        '@omlish-magic-test "foo"',
        '# @omlish-magic-test "bar"',
    ]),

    '@omlish-magic-test "foo", "bar"',

    '@omlish-magic-test {"foo": 1, "bar": 2}',

    '\n'.join([
        '@omlish-magic-test {',
        '#     "foo": 1,',
        '#     "bar": 2',
        '# }',
    ]),
]

C_LINE_TESTS = [
    '@omlish-magic-test',

    '\n'.join([
        '@omlish-magic-test "foo"',
        '// @omlish-magic-test "bar"',
    ]),

    '\n'.join([
        '@omlish-magic-test {',
        '//     "foo": 1,',
        '//     "bar": 2',
        '// }',
    ]),
]

C_BLOCK_TESTS = [
    '@omlish-magic-test',

    '\n'.join([
        '@omlish-magic-test "foo"',
        '@omlish-magic-test "bar"',
    ]),

    '\n'.join([
        '@omlish-magic-test {',
        '    "foo": 1,',
        '    "bar": 2',
        '}',
    ]),
]


def chop_magic_block(
        magic_key: str,
        first_prefix: str,
        rest_prefix: str,
        lines: ta.Iterable[str],
) -> list[str] | None:
    out: list[str] = []
    for i, l in enumerate(lines):
        if not i:
            if not l.startswith(first_prefix + magic_key):
                return None
            out.append(l[len(first_prefix) + len(magic_key) + 1:])
        else:
            if not l.startswith(rest_prefix):
                return None
            out.append(l[len(rest_prefix):])
    return out


def find_magic(
        magic_key_prefix: str,
        first_prefix: str,
        rest_prefix: str,
        lines: ta.Sequence[str],
        file: str,
) -> list[Magic]:
    out: list[Magic] = []

    start = 0
    while start < len(lines):
        start_line = lines[start]
        if not start_line.startswith(first_prefix + magic_key_prefix):
            start += 1
            continue

        key = start_line[len(first_prefix):].split()[0]

        end = start
        magic: Magic | None = None
        while end < len(lines):
            block_lines = chop_magic_block(
                key,
                first_prefix,
                rest_prefix,
                lines[start:end + 1],
            )
            if block_lines is None:
                raise Exception(f'Failed to find magic block terminator : {file=} {start=} {end=}')

            block_src = ''.join(['(', *block_lines, ')'])
            try:
                prepared = compile(block_src, '<magic>', 'eval')
            except SyntaxError:
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

    for test_file, first_prefix, rest_prefix in [
        (PY_TEST_FILE.replace('%', '@'), '# ', '# '),
        # (C_LINE_TESTS, '// ', '// '),
        # (C_BLOCK_TESTS, '/* ', ''),
    ]:
        magics = find_magic(
            MAGIC_KEY_PREFIX,
            first_prefix,
            rest_prefix,
            test_file.splitlines(keepends=True),
            'test-file',
        )
        print(magics)
