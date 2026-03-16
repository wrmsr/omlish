import json
import uuid

from omlish import marshal as msh

from ...metadata import MessageUuid
from ..types import AiDeltas
from ..types import ContentAiDelta


def test_marshal():
    o = [
        ContentAiDelta('hi'),
        ContentAiDelta('bye').with_metadata(
            MessageUuid(uuid.uuid4()),
        ),
    ]
    v = msh.marshal(o, AiDeltas)
    s = json.dumps(v)
    j = json.loads(s)
    u = msh.unmarshal(j, AiDeltas)
    assert list(u) == o
    assert o[1].metadata[MessageUuid].v == u[1].metadata[MessageUuid].v
