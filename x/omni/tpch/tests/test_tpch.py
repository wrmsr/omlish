import itertools

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
