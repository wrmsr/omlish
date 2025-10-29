import itertools
import textwrap

import pytest

from omlish import check

from .. import base as ba
from .. import core as co
from .. import parsers as pa
from ..meta import META_GRAMMAR
from ..meta import MetaGrammarRuleVisitor
from ..utils import fix_grammar_ws
from ..utils import only_match_rules
from ..utils import strip_insignificant_match_rules


@pytest.mark.parametrize('src', [chr(x) for x in itertools.chain(range(0x41, 0x5b), range(0x61, 0x7b))])
def test_alpha(src):
    m = check.not_none(co.CORE_GRAMMAR.parse(src, 'ALPHA'))
    assert src[m.start:m.end] == src


@pytest.mark.parametrize('src', [
    '',
    *[x*y for x, y in itertools.product([1, 2], [' ', '\t', '\r\n ', '\r\n\t'])],
])
def test_lwsp(src):
    m = co.CORE_GRAMMAR.parse(src, 'LWSP')
    print(m)
    # [m] = CORE_GRAMMAR.parse(src, 'LWSP')
    # assert src[m.start:m.end] == src
