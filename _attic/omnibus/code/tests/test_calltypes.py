import sys

from .. import calltypes as calltypes_


def test_posonly():
    if sys.version_info[1] > 7:
        assert callable(calltypes_.CallTypes.posonly)
