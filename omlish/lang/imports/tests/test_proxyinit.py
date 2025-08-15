def test_auto_proxy_init():
    from . import foo2  # noqa

    for k in ('math', 'qux', 'ghi'):
        assert k not in foo2.__dict__

    assert foo2.math.pi < 4
    assert foo2.qux.jarf == 420
    assert foo2.ghi == 2
