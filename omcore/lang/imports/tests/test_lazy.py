from ..lazy import lazy_import


def test_lazy():
    sys = lazy_import('sys')
    assert sys().version_info[0] == 3
