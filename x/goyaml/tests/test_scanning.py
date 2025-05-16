import os.path

import yaml

from .. import scanning


def test_scanning():
    with open(os.path.join(os.path.dirname(__file__), 'sample.yaml')) as f:
        src = f.read()

    doc = yaml.safe_load(src)  # noqa

    tks = scanning.tokenize(src)
    for tk in tks:
        print(tk)
