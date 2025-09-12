import itertools

import pytest

from ..core import CORE_RULES
from ..base import parse


@pytest.mark.parametrize('src', [chr(x) for x in itertools.chain(range(0x41, 0x5b), range(0x61, 0x7b))])
def test_alpha(src):
    ms = list(parse(CORE_RULES['ALPHA'], src))
    assert ms
