from ..lazy import lazy_import
from ..lazy import proxy_import


def test_lazy():
    sys = lazy_import('sys')
    assert sys().version_info[0] == 3


def test_proxy():
    sys = proxy_import('sys')
    assert sys.version_info[0] == 3
