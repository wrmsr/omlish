import sys

from .. import protocols


def test_protos():
    assert isinstance(sys._getframe(1), protocols.FrameProtocol)
    assert isinstance(sys._getframe(1).f_code, protocols.CodeProtocol)
    assert not isinstance('banana', protocols.FrameProtocol)
    assert not isinstance('banana', protocols.CodeProtocol)
