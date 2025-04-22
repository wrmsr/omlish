from omlish import marshal as msh
from omlish.secrets.tests.harness import HarnessSecrets

from ..completion import OpenaiCompletionService
from ....completion import CompletionRequest
from ....standard import ApiKey


def test_openai(harness):
    llm = OpenaiCompletionService(ApiKey(harness[HarnessSecrets].get_or_skip('openai_api_key').reveal()))

    req: CompletionRequest = CompletionRequest.new(
        'Is water dry?',
    )

    rm = msh.marshal(req)
    print(rm)
    req2 = msh.unmarshal(rm, CompletionRequest)
    print(req2)

    resp = llm(req)
    print(resp)
    assert resp.text

