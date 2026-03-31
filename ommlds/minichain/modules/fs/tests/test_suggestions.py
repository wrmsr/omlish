import sys

from ..suggestions import get_path_suggestions


def test_suggest():
    print(get_path_suggestions(sys.executable + 'x'))
