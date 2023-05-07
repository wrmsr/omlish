from .. import threading as othr


def test_tlc():
    class C(othr.ThreadLocalContext):
        def __init__(self, v):
            super().__init__()
            self.v = v

    with C(0):
        assert C.current().v == 0
        with C(1):
            assert C.current().v == 1
