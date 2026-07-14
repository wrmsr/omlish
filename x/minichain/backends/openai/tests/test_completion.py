import pytest

from omcore import lang
from omcore import marshal as msh
from omcore.http import all as http
from omcore.secrets.tests.harness import HarnessSecrets

from ....completion import CompletionRequest
from ....standard import ApiKey
from ..completion import OpenaiCompletionService


@pytest.mark.online
def test_openai(harness):
    llm = OpenaiCompletionService(
        ApiKey(harness[HarnessSecrets].get_or_skip('openai_api_key').reveal()),
        http_client=http.SyncAsyncHttpClient(http.client()),
    )

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
