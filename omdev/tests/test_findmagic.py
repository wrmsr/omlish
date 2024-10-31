"""
TODO:
 - comment modes: #, //, /* */
 - syntax modes: json, py
"""
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


def test_multiline_magic():
    print()
    for s in PY_TESTS:
        s = '#' + s
        print(s)
        print()

        lines = s.splitlines(keepends=True)
