import os.path

from ..parsing import parse


def test_sample():
    with open(os.path.join(os.path.dirname(__file__), 'sample.edn')) as f:
        src = f.read()

    v = parse(src)
    print(v)
