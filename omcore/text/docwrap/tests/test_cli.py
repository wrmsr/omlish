from ..cli import _main as cli_main
from ..cli import wrap_cli_text


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


def test_wrap_cli_text_stdin_range():
    given = (
        'line 1\n'
        'line 2\n'
        'line 3 line 3 line 3 line 3 line 3 line 3 line 3 line 3\n'
        'line 4 line 4 line 4 line 4 line 4 line 4 line 4 line 4\n'
        'line 5\n'
    )

    expected = (
        'line 1\n'
        'line 2\n'
        'line 3 line 3 line 3 line 3 line 3 line 3\n'
        'line 3 line 3 line 4 line 4 line 4 line 4\n'
        'line 4 line 4 line 4 line 4\n'
        'line 5\n'
    )

    actual = wrap_cli_text(
        given,
        width=45,
        start_line=3,
        end_line=4,
    )

    assert actual == expected


def test_wrap_cli_text2():
    given = (
        'line 1\n'
        'line 2 line 2 line 2 line 2 line 2 line 2 line 2 line 2\n'
        'line 3\n'
    )

    expected = (
        'line 1\n'
        'line 2 line 2 line 2 line 2 line 2\n'
        'line 2 line 2 line 2\n'
        'line 3\n'
    )

    actual = wrap_cli_text(
        given,
        width=35,
        start_line=2,
        end_line=2,
    )

    assert actual == expected


def test_wrap_cli_text_docstring_body_range_preserves_closing_quote():
    given = (
        'def f():\n'
        '    """Doc.\n'
        '    alpha beta gamma delta epsilon zeta eta theta iota kappa lambda\n'
        '    mu nu xi omicron pi rho sigma tau upsilon phi chi psi omega\n'
        '    """\n'
    )

    expected = (
        'def f():\n'
        '    """Doc.\n'
        '    alpha beta gamma delta epsilon zeta eta theta\n'
        '    iota kappa lambda mu nu xi omicron pi rho sigma\n'
        '    tau upsilon phi chi psi omega\n'
        '    """\n'
    )

    actual = wrap_cli_text(
        given,
        width=52,
        start_line=3,
        end_line=4,
    )

    assert actual == expected
