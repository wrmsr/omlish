from omlish import lang
from omlish import marshal as msh
from omlish.secrets.tests.harness import HarnessSecrets

from .....completion import CompletionRequest
from .....standard import ApiKey
from ..completion import OpenaiCompletionService


def test_openai(harness):
    llm = OpenaiCompletionService(ApiKey(harness[HarnessSecrets].get_or_skip('openai_api_key').reveal()))

    req: CompletionRequest = CompletionRequest(
        'Is water dry?',
    )

    rm = msh.marshal(req)
    print(rm)
    req2 = msh.unmarshal(rm, CompletionRequest)
    print(req2)

    resp = lang.sync_await(llm.invoke(req))
    print(resp)
    assert resp.v
