import typing as ta

from .dbs import TestingDbs


def test_dbs(harness):
    dbs = harness[TestingDbs]
    assert isinstance(dbs.specs(), ta.Mapping)
