import typing as ta  # noqa

from omlish.testing import pytest as ptu

from .. import wtp
from .data import WIKI_FILES


##


@ptu.skip.if_cant_import('wikitextparser')
def test_dom():
    for n, src in WIKI_FILES.items():
        print(n)

        root = wtp.parse_tree(src)  # noqa
