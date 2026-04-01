import abc
import asyncio
import time
import typing as ta


##


class ChatClient(abc.ABC):
    """Abstract base class for chat completion clients."""

    @abc.abstractmethod
    def stream_chat_completion(self, messages: list, model: str) -> ta.AsyncGenerator[dict]:
        """
        Stream chat completion responses.

        Args:
            messages: List of message dictionaries with 'role' and 'content'
            model: Model identifier to use

        Yields:
            Dictionary chunks in OpenAI's format
        """

        pass


class OpenaiChatClient(ChatClient):
    """OpenAI chat client implementation."""

    async def stream_chat_completion(self, messages: list, model: str) -> ta.AsyncGenerator[dict]:
        """Stream chat completion from OpenAI."""

        # stream = self.client.chat.completions.create(
        #     model=model,
        #     messages=messages,
        #     stream=True
        # )
        #
        # for chunk in stream:
        #     yield chunk

        raise NotImplementedError


class MockChatClient(ChatClient):
    """Mock chat client for testing without API calls."""

    async def stream_chat_completion(self, messages: list, model: str) -> ta.AsyncGenerator[dict]:
        """Stream a mock chat completion response."""

        mock_response = "This is a mock response. Set OPENAI_API_KEY to use real OpenAI API."

        for i, char in enumerate(mock_response):
            chunk = {
                'id': 'chatcmpl-mock',
                'object': 'chat.completion.chunk',
                'created': int(time.time()),
                'model': model,
                'choices': [{
                    'index': 0,
                    'delta': {'content': char},
                    'finish_reason': None
                }]
            }
            yield chunk
            await asyncio.sleep(0.05)

        final_chunk = {
            'id': 'chatcmpl-mock',
            'object': 'chat.completion.chunk',
            'created': int(time.time()),
            'model': model,
            'choices': [{
                'index': 0,
                'delta': {},
                'finish_reason': 'stop'
            }]
        }
        yield final_chunk
