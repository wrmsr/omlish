from .. import dispatch


def test_dispatch():
    @dispatch.function
    def f(x: object):
        return 'object'

    @f.register
    def f_int(x: int):
        return 'int'

    @f.register
    def f_int(x: str):
        return 'str'

    assert f(1.) == 'object'
    assert f(1) == 'int'
    assert f('1') == 'str'
