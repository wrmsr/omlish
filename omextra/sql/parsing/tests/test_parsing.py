from ..parsing import parse_stmt


def test_parse_stmt():
    for stmt in [
        'select 1;',
        'select x from y;',
    ]:
        print(parse_stmt(stmt))
