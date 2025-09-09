from ..proxy import proxy_import


def test_proxy():
    sys = proxy_import('sys')
    assert sys.version_info[0] == 3
