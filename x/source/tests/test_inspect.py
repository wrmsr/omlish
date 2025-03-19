from omlish import lang

from ..inspect import find_source


def test_find_source() -> None:
    fs = find_source(lang.Abstract)
    print(fs)
