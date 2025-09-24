import sys

from ..read import execute_read_tool
from ..read import get_suggestions
from ..read import is_binary_file


def test_is_binary():
    assert is_binary_file(sys.executable)


def test_suggest():
    print(get_suggestions(sys.executable + 'x'))


def test_read():
    print()
    print(execute_read_tool(__file__, line_offset=14, num_lines=3))
