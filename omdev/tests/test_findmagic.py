"""
TODO:
 - comment modes: #, //, /* */
 - syntax modes: json, py
"""
import typing as ta


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


def unmagic_lines(
        magic: str,
        first_prefix: str,
        rest_prefix: str,
        lines: ta.Iterable[str],
) -> list[str] | None:
    out: list[str] = []
    for i, l in enumerate(lines):
        if not i:
            if not l.startswith(first_prefix + magic):
                return None
            out.append(l[len(first_prefix) + len(magic) + 1:])
        else:
            if not l.startswith(rest_prefix):
                return None
            out.append(l[len(rest_prefix):])
    return out


def test_multiline_magic():
    print()

    for tests, first_prefix, rest_prefix in [
        (PY_TESTS, '# ', '# '),
        (C_LINE_TESTS, '// ', '// '),
        (C_BLOCK_TESTS, '/* ', ''),
    ]:
        for s in tests:
            s = first_prefix + s
            print(s)
            print()

            lines = s.splitlines(keepends=True)
            start = 0
            for end in range(start, len(lines)):
                block_lines = unmagic_lines(
                    TEST_MAGIC,
                    first_prefix,
                    rest_prefix,
                    lines[start:end + 1],
                )
                if block_lines is None:
                    raise Exception('Failed to find magic block terminator')

                block_src = ''.join(['(', *block_lines, ')'])
                try:
                    code = compile(block_src, '<magic>', 'eval')
                except SyntaxError:
                    continue

                print(block_src)
                block_val = eval(code)  # noqa
                print(block_val)
                break
