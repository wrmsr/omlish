import importlib.resources
import typing as ta  # noqa

from .. import wtp


##


def test_dom():
    src = importlib.resources.files(__package__).joinpath('data', 'test.wiki').read_text()

    root = wtp.parse_tree(src)  # noqa

    print('!! DONE')
