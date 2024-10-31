"""
TODO:
 - comment modes: #, //, /* */
 - syntax modes: json, py
"""
import typing as ta


TEST_MAGIC = '@omlish-magic-test'
PY_COMMENT_PREFIX = '# '

PY_TESTS = [
    ' @omlish-magic-test',
    '\n'.join([
        ' @omlish-magic-test',
        '"bar"',
    ]),
    '\n'.join([
        ' @omlish-magic-test',
        'bar',
    ]),

    ' @omlish-magic-test "foo"',
    '\n'.join([
        ' @omlish-magic-test "foo"',
        '"bar"',
    ]),
    '\n'.join([
        ' @omlish-magic-test "foo"',
        'bar',
    ]),

    '\n'.join([
        ' @omlish-magic-test "foo"',
        '# @omlish-magic-test "bar"',
    ]),

    ' @omlish-magic-test "foo", "bar"',

    ' @omlish-magic-test {"foo": 1, "bar": 2}',

    '\n'.join([
        ' @omlish-magic-test {',
        '#     "foo": 1,',
        '#     "bar": 2',
        '# }',
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

    for s in PY_TESTS:
        s = '#' + s
        print(s)
        print()

        lines = s.splitlines(keepends=True)
        start = 0
        assert lines[start].startswith(PY_COMMENT_PREFIX + TEST_MAGIC)
        for end in range(start, len(lines)):
            block_lines = unmagic_lines(
                TEST_MAGIC,
                '# ',
                '# ',
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
            block_val = eval(code)
            print(block_val)
            break
