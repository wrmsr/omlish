import typing as ta

from .dbs import Dbs


def test_dbs(harness):
    dbs = harness[Dbs]
    assert isinstance(dbs.specs(), ta.Mapping)
