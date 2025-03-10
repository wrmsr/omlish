import pytest  # noqa

from omlish import marshal as msh
from omlish.formats import json

from ... import minichain as mc


# @pytest.mark.xfail(reason='marshal unions')
def test_requests():
    for req in [
        mc.ChatRequest.new(
            [mc.UserMessage('foo')],
        ),
        # mc.ChatRequest.new(
        #     [mc.UserMessage('foo')],
        #     mc.Max
        #
        # ),
    ]:
        print(req)

        req_m = msh.marshal(req)
        req_j = json.dumps_pretty(req_m)
        print(req_j)

        req_u = msh.unmarshal(json.loads(req_j), mc.ChatRequest)
        print(req_u)

        # assert req_u == req
