import pytest

from omlish import lang
from omlish.http import all as http

from .....chat.messages import UserMessage
from .....services import Request
from ..chat import OllamaChatChoicesService
from ..chat import OllamaChatChoicesStreamService


@pytest.mark.not_docker_guest
@pytest.mark.high_mem
@pytest.mark.asyncs('asyncio')
async def test_chat():
    try:
        http.request(OllamaChatChoicesService.DEFAULT_API_URL.v)
    except http.HttpClientError:
        pytest.skip('No ollama server')

    with lang.maybe_managing(OllamaChatChoicesService(
        http_client=http.SyncAsyncHttpClient(http.client()),
    )) as llm:
        q = 'Is a bird a mammal?'

        resp = await llm.invoke(Request([UserMessage(q)]))
        print(resp)
        assert resp.v


@pytest.mark.not_docker_guest
@pytest.mark.high_mem
@pytest.mark.asyncs('asyncio')
async def test_chat_stream():
    try:
        http.request(OllamaChatChoicesService.DEFAULT_API_URL.v)
    except http.HttpClientError:
        pytest.skip('No ollama server')

    with lang.maybe_managing(OllamaChatChoicesStreamService(
        http_client=http.SyncAsyncHttpClient(http.client()),
    )) as llm:
        q = 'Is a bird a mammal?'

        async with (resp := await llm.invoke(Request([UserMessage(q)]))).v as it:  # noqa
            async for o in it:
                print(o)
