import itertools

import pytest

from omlish import check

from ..core import CORE_RULES
from ..base import Grammar


CORE_GRAMMAR = Grammar(CORE_RULES)


@pytest.mark.parametrize('src', [chr(x) for x in itertools.chain(range(0x41, 0x5b), range(0x61, 0x7b))])
def test_alpha(src):
    m = check.not_none(CORE_GRAMMAR.parse(src, 'ALPHA'))
    assert src[m.start:m.end] == src


@pytest.mark.parametrize('src', [
    '',
    *[x*y for x, y in itertools.product([1, 2], [' ', '\t', '\r\n ', '\r\n\t'])],
])
def test_lwsp(src):
    m = CORE_GRAMMAR.parse(src, 'LWSP')
    print(m)
    # [m] = CORE_GRAMMAR.parse(src, 'LWSP')
    # assert src[m.start:m.end] == src
