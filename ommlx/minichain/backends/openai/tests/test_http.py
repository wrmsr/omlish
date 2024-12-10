"""
{
  "frequency_penalty": 0.0,
  "max_tokens": 64,
  "messages": [
    {
      "content": "Is water dry?",
      "role": "user"
    }
  ],
  "model": "gpt-4o",
  "presence_penalty": 0.0,
  "stream": false,
  "temperature": 0.1,
  "top_p": 1
}
"""
import typing as ta

import pytest

from omlish import dataclasses as dc
from omlish.http import all as hu
from omlish.formats import json
from omlish.secrets.tests.harness import HarnessSecrets


@dc.dataclass(frozen=True)
class HttpOpenaiChatCompletionRequest:
    messages: ta.Sequence[ta.Any]
    model: str | None = None
    frequency_penalty: float | None = None
    logit_bias: ta.Mapping[str, int] | None = None
    logprobs: bool | None = None
    top_logprobs: int | None = None
    max_tokens: int | None = None
    n: int | None = None
    presence_penalty: float | None = None
    response_format: ta.Any | None = None
    seed: int | None = None
    service_tier: str | None = None
    stop: str | ta.Sequence[str] | None = None
    stream: bool | None = None
    stream_options: ta.Any | None = None
    temperature: float | None = None
    top_p: float | None = None
    tools: ta.Sequence[ta.Any] | None = None
    tool_choice: ta.Any | None = None
    parallel_tool_calls: ta.Any | None = None


@dc.dataclass(frozen=True)
class HttpOpenaiChatCompletionResponse:
    id: str
    choices: ta.Sequence[ta.Any] | None = None
    created: int | None = None
    model: str | None = None
    service_tier: str | None = None
    system_fingerprint: str | None = None
    object: str | None = None
    usage: ta.Any | None = None


@pytest.mark.parametrize('cli_cls', [hu.UrllibHttpClient, hu.HttpxHttpClient])
def test_openai_http(harness, cli_cls):
    key = harness[HarnessSecrets].get_or_skip('openai_api_key')

    req = HttpOpenaiChatCompletionRequest(
        model='gpt-4o-mini',
        messages=[
            dict(
                role='user',
                content='Hi!',
            ),
        ],
    )

    with cli_cls() as cli:
        print(cli.request(hu.HttpRequest(
            'https://api.openai.com/v1/chat/completions',
            headers={
                hu.consts.HEADER_CONTENT_TYPE: hu.consts.CONTENT_TYPE_JSON,
                hu.consts.HEADER_AUTH: hu.consts.format_bearer_auth_header(key.reveal()),
            },
            data=json.dumps({
                k: v
                for k, v in dc.asdict(req).items()
                if v is not None
            }).encode('utf-8'),
        )).data)
