from ..traversal import yield_importable


def test_yield_importable():
    base_pkg = __package__.rpartition('.')[0]

    lst = list(yield_importable(base_pkg))
    assert base_pkg + '.traversal' in lst
    assert __name__ not in lst

    lst = list(yield_importable(base_pkg, recursive=True))
    assert base_pkg + '.traversal' in lst
    assert __name__ in lst
