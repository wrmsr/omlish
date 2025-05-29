"""
https://docs.anthropic.com/en/api/getting-started
"""
import pytest

from omlish.formats import json
from omlish.http import all as hu
from omlish.secrets.tests.harness import HarnessSecrets


@pytest.mark.parametrize('cli_cls', [hu.UrllibHttpClient, hu.HttpxHttpClient])
def test_anthropic_http(harness, cli_cls):
    key = harness[HarnessSecrets].get_or_skip('anthropic_api_key')

    with cli_cls() as cli:
        print(cli.request(hu.HttpRequest(
            'https://api.anthropic.com/v1/messages',
            headers={
                hu.consts.HEADER_CONTENT_TYPE: hu.consts.CONTENT_TYPE_JSON,
                b'x-api-key': key.reveal().encode('utf-8'),
                b'anthropic-version': b'2023-06-01',
            },
            data=json.dumps(dict(
                model='claude-3-5-sonnet-20241022',
                max_tokens=1024,
                messages=[
                    dict(
                        role='user',
                        content='Hi!',
                    ),
                ],
            )).encode('utf-8'),
        )).data)
