from omlish import marshal as msh
from omlish.formats import json

from ... import minichain as mc


def test_requests():
    req: mc.ChatRequest
    for req in [
        mc.ChatRequest(
            [mc.UserMessage('foo')],
        ),
        mc.ChatRequest(
            [mc.UserMessage('foo')],
            [mc.MaxTokens(420)],
        ),
    ]:
        print(req)

        req_m = msh.marshal(req)
        req_j = json.dumps_pretty(req_m)
        print(req_j)

        req_u = msh.unmarshal(json.loads(req_j), mc.ChatRequest)
        print(req_u)

        # assert req_u == req
