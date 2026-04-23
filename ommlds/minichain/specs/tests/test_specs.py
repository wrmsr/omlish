from omlish import marshal as msh

from ..types import BackendSpec
from ..types import FirstInWinsBackendSpec
from ..types import ModelBackendSpec
from ..types import RetryBackendSpec


def test_marshal():
    for bs in [
        ModelBackendSpec('hi'),
        RetryBackendSpec(ModelBackendSpec('hi')),
        FirstInWinsBackendSpec([
            ModelBackendSpec('hi'),
            RetryBackendSpec(ModelBackendSpec('bye')),
        ]),
    ]:
        mbs = msh.marshal(bs, BackendSpec)
        print(mbs)
        bs2 = msh.unmarshal(mbs, BackendSpec)
        print(bs2)
