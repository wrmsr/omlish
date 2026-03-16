import json
import uuid

from omlish import marshal as msh

from ..metadata import AiDeltaMessageUuid
from ..types import AiDeltas
from ..types import ContentAiDelta


def test_marshal():
    o = [
        ContentAiDelta('hi'),
        ContentAiDelta('bye').with_metadata(
            AiDeltaMessageUuid(uuid.uuid4()),
        ),
    ]
    v = msh.marshal(o, AiDeltas)
    s = json.dumps(v)
    j = json.loads(s)
    u = msh.unmarshal(j, AiDeltas)
    assert list(u) == o
    assert o[1].metadata[AiDeltaMessageUuid].v == u[1].metadata[AiDeltaMessageUuid].v
