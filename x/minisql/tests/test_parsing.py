from ..parsing import parse_stmt


def test_parse_stmt():
    print(parse_stmt('select 1;'))
