import os.path

import pytest

from ..parsing import parse


@pytest.mark.xfail(reason='FIXME')
def test_sample():
    with open(os.path.join(os.path.dirname(__file__), 'sample.edn')) as f:
        src = f.read()

    v = parse(src)
    print(v)
