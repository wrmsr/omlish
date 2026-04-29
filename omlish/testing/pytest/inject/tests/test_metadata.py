from ..metadata import FunctionRunMetadata
from ..metadata import ModuleRunMetadata
from ..metadata import SessionRunMetadata


def _test_metadata(harness):
    print(harness[SessionRunMetadata])
    print(harness[ModuleRunMetadata])
    print(harness[FunctionRunMetadata])


def test_metadata1(harness):
    _test_metadata(harness)


def test_metadata2(harness):
    _test_metadata(harness)
