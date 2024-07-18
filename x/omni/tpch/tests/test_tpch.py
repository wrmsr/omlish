import itertools
import os.path

import pytest

from . import data
from .. import ents as ents_  # noqa
from .. import gens as gens_  # noqa
from .. import rand as rand_  # noqa
from .. import text as text_  # noqa


@pytest.mark.xfail()
def test_tpch():
    cg = gens_.CustomerGenerator(10, 1, 20)
    got = list(itertools.islice(cg, 2))
    assert got == data.EXPECTED_CUSTOMERS

    rg = gens_.RegionGenerator()
    got = list(itertools.islice(rg, 2))
    assert got == data.EXPECTED_REGIONS

    cg = gens_.CustomerGenerator(10, 1, 20)
    for c in cg:  # noqa
        pass


def test_rand():
    print(rand_.RandomAlphaNumeric(420, 100, 1).next_value())


def test_cext():
    for fn in os.listdir(os.path.join(os.path.dirname(__file__), '..')):
        if os.path.isfile(fn) and fn.endswith('.so'):
            os.unlink(fn)

    from omdev.exts.importhook import install as _install_ext_hook  # noqa
    _install_ext_hook()  # noqa

    from .. import _tpch  # noqa
    print(_tpch.gen_text_pool())
