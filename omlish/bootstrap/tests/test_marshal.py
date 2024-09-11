import os

import pytest  # noqa

from ... import marshal as msh
from ..base import Bootstrap
from ..harness import bootstrap


@pytest.mark.skip
def test_marshal():
    cfgs = msh.unmarshal([
        {'env': {'vars': [{'TEST_BOOTSTRAP_MARSHAL': '420'}]}},
        {'print_pid': {'enable': True}},
    ], list[Bootstrap.Config])

    with bootstrap(*cfgs):
        assert os.environ['TEST_BOOTSTRAP_MARSHAL'] == '420'
