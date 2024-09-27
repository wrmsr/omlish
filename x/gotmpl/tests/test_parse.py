from ..parse import parse


def test_parse():
    for s in [
        'hi',
    ]:
        t = parse('-', s)['-']
        print(t)
