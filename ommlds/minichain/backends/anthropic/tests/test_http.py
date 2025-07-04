"""
https://docs.anthropic.com/en/api/getting-started
"""
import pytest

from omlish.formats import json
from omlish.http import all as hu
from omlish.secrets.tests.harness import HarnessSecrets

from ....chat.messages import UserMessage
from ....services import Request
from ....standard import ApiKey
from ....standard import ModelName
from ..chat import AnthropicChatChoicesService


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


def test_anthropic_chat(harness):
    key = harness[HarnessSecrets].get_or_skip('anthropic_api_key')
    svc = AnthropicChatChoicesService(ApiKey(key.reveal()))
    resp = svc.invoke(Request([UserMessage('hi')]))
    print(resp.v)


def test_anthropic_chat_model_name(harness):
    key = harness[HarnessSecrets].get_or_skip('anthropic_api_key')
    svc = AnthropicChatChoicesService(ApiKey(key.reveal()), ModelName('claude-sonnet-4-20250514'))
    resp = svc.invoke(Request([UserMessage('hi')]))
    print(resp.v)
