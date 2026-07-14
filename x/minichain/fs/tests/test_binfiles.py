import sys

from ..binfiles import is_binary_file


def test_is_binary():
    assert is_binary_file(sys.executable)
