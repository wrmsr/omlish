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
import pytest

from omlish import http as hu
from omlish.formats import json
from omlish.secrets.tests.harness import HarnessSecrets


@pytest.mark.parametrize('cli_cls', [hu.UrllibHttpClient, hu.HttpxHttpClient])
def test_openai_http(harness, cli_cls):
    key = harness[HarnessSecrets].get_or_skip('openai_api_key')

    url = 'https://api.openai.com/v1/chat/completions'

    dct = dict(
        model='gpt-4o-mini',
        messages=[
            dict(
                role='user',
                content='Hi!',
            ),
        ],
    )
    data = json.dumps(dct).encode('utf-8')

    headers = {
        hu.consts.HEADER_CONTENT_TYPE: hu.consts.CONTENT_TYPE_JSON,
        hu.consts.HEADER_AUTH: hu.consts.format_bearer_auth_header(key.reveal()),
    }

    with cli_cls() as cli:
        print(cli.request(hu.HttpRequest(
            url,
            headers=headers,
            data=data,
        )).data)
