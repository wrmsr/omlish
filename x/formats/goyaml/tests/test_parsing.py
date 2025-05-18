import os.path

import yaml

from .. import parsing


def test_parsing():
    with open(os.path.join(os.path.dirname(__file__), 'sample.yaml')) as f:
        src = f.read()

    doc = yaml.safe_load(src)  # noqa

    obj, err = parsing.parse_str(
        src,
        parsing.ParseMode(0),
    )

    print(obj)
    print(repr(obj))
