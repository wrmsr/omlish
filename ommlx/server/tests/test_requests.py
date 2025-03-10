import pytest  # noqa

from omlish import marshal as msh
from omlish.formats import json

from ... import minichain as mc


@pytest.mark.xfail('marshal unions')
def test_requests():
    prompt = 'foo'
    req = mc.ChatRequest.new(
        [mc.UserMessage(prompt)],
    )

    req_m = msh.marshal(req)
    req_j = json.dumps_pretty(req_m)

    print(req_j)
