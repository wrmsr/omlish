from ..parse import parse


def test_parse():
    for s in [
        'hi',
        '{{ hi }} there',
    ]:
        t = parse('-', s)['-']
        print(t)
