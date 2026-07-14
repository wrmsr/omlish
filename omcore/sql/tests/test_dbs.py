import typing as ta

from .harness import HarnessDbs


def test_dbs(harness):
    dbs = harness[HarnessDbs]
    assert isinstance(dbs.specs(), ta.Mapping)
