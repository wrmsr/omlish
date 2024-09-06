import typing as ta  # noqa

from .. import wtp
from .data import WIKI_FILES


##


def test_dom():
    for n, src in WIKI_FILES.items():
        print(n)

        root = wtp.parse_tree(src)  # noqa
