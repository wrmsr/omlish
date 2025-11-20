from ..cli import _main as cli_main


def test_cli(tmp_path):
    given = """\
line 1
line 2

line 4 line 4 line 4 line 4 line 4 line 4 line 4 line 4 line 4 line 4 line 4 line 4

line 6 line 6 line 6 line 6 line 6 line 6 line 6 line 6 line 6 line 6 line 6 line 6

line 5
line 6 line 6 line 6 line 6 line 6 line 6 line 6 line 6 line 6 line 6 line 6 line 6
line 7

line 8
line 9
"""

    expected = """\
line 1 line 2

line 4 line 4 line 4 line 4 line 4 line
4 line 4 line 4 line 4 line 4 line 4
line 4

line 6 line 6 line 6 line 6 line 6 line
6 line 6 line 6 line 6 line 6 line 6
line 6

line 5 line 6 line 6 line 6 line 6 line
6 line 6 line 6 line 6 line 6 line 6
line 6 line 6 line 7

line 8 line 9
"""

    with open(fp := str(tmp_path / 'test.txt'), 'w') as f:
        f.write(given)

    cli_main([
        fp,
        '-i',
        '-w', '40',
    ])

    with open(fp) as f:
        actual = f.read()

    assert actual == expected


def test_cli_range(tmp_path):
    given = """\
line 1
line 2

line 4 line 4 line 4 line 4 line 4 line 4 line 4 line 4 line 4 line 4 line 4 line 4

line 6 line 6 line 6 line 6 line 6 line 6 line 6 line 6 line 6 line 6 line 6 line 6

line 5
line 6 line 6 line 6 line 6 line 6 line 6 line 6 line 6 line 6 line 6 line 6 line 6
line 7

line 8
line 9
"""

    expected = """\
line 1
line 2

line 4 line 4 line 4 line 4 line 4 line 4 line 4 line 4 line 4 line 4 line 4 line 4

line 6 line 6 line 6 line 6 line 6 line
6 line 6 line 6 line 6 line 6 line 6
line 6

line 5 line 6 line 6 line 6 line 6 line
6 line 6 line 6 line 6 line 6 line 6
line 6 line 6 line 7

line 8
line 9
"""

    with open(fp := str(tmp_path / 'test.txt'), 'w') as f:
        f.write(given)

    cli_main([
        fp,
        '-i',
        '-w', '40',
        '-s', '5',
        '-e', '11',
    ])

    with open(fp) as f:
        actual = f.read()

    assert actual == expected
