import pytest

from ....chat.messages import UserMessage
from ....chat.services import ChatRequest
from ....completion import CompletionRequest
from ....services import Request
from ....standard import ModelPath
from ..transformers import TransformersChatService
from ..transformers import TransformersCompletionService
from ..transformers import TransformersPipelineKwargs


@pytest.mark.not_docker_guest
@pytest.mark.high_mem
def test_transformers_completion():
    with TransformersCompletionService(
        ModelPath('Qwen/Qwen2-0.5B'),
        TransformersPipelineKwargs(dict(
            max_new_tokens=20,
            # device=None,
        )),
    ) as llm:
        resp = llm.invoke(CompletionRequest('Is water dry?'))
        print(resp)
        assert resp.v

        resp = llm.invoke(Request('Is water dry?'))
        print(resp)
        assert resp.v


@pytest.mark.not_docker_guest
@pytest.mark.high_mem
def test_transformers_chat():
    with TransformersChatService(
        ModelPath('meta-llama/Llama-3.2-1B-Instruct'),
        TransformersPipelineKwargs(dict(
            max_new_tokens=20,
            # device=None,
        )),
    ) as llm:
        resp = llm.invoke(ChatRequest([UserMessage('Is water dry?')]))
        print(resp)
        assert resp


# @pytest.mark.not_docker_guest
# @pytest.mark.high_mem
# def test_transformers_chat_phi4_tools():
#     llm = TransformersChatService(
#         ModelPath('microsoft/Phi-4-mini-instruct'),
#         TransformersPipelineKwargs(dict(
#             max_new_tokens=20,
#             # device=None,
#         )),
#     )
#
#     resp = llm.invoke(ChatRequest.new([UserMessage('Is water dry?')]))
#     print(resp)
#     assert resp
