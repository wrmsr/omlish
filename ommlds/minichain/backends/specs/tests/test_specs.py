from omlish import marshal as msh

from ....models.configs import ModelName
from ..types import BackendSpec
from ..types import FirstInWinsBackendSpec
from ..types import ModelBackendSpec
from ..types import RetryBackendSpec


def test_marshal():
    for bs in [
        ModelBackendSpec(ModelName('hi')),
        RetryBackendSpec(ModelBackendSpec(ModelName('hi'))),
        FirstInWinsBackendSpec([
            ModelBackendSpec(ModelName('hi')),
            RetryBackendSpec(ModelBackendSpec(ModelName('bye'))),
        ]),
    ]:
        mbs = msh.marshal(bs, BackendSpec)
        print(mbs)
        bs2 = msh.unmarshal(mbs, BackendSpec)
        print(bs2)
