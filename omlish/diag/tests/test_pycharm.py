from ..pycharm import PycharmRemoteDebugger


def test_remote_debugger():
    for prd, s in [
        (PycharmRemoteDebugger(None, 420), '420'),
        (PycharmRemoteDebugger('foo', 420), 'foo:420'),
        (PycharmRemoteDebugger(None, 420, '123.abc'), '@123.abc:420'),
        (PycharmRemoteDebugger('foo', 420, '123.abc'), '@123.abc:foo:420'),
    ]:
        assert str(prd) == s
        assert PycharmRemoteDebugger.parse(s) == prd
