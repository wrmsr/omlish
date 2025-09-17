import pytest

from omlish import lang

from .....chat.choices.services import ChatChoicesRequest
from .....chat.messages import UserMessage
from .....completion import CompletionRequest
from .....models.configs import ModelPath
from .....services import Request
from ..transformers import TransformersChatChoicesService
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
        resp = lang.sync_await(llm.invoke(CompletionRequest('Is water dry?')))
        print(resp)
        assert resp.v

        resp = lang.sync_await(llm.invoke(Request('Is water dry?')))
        print(resp)
        assert resp.v


@pytest.mark.not_docker_guest
@pytest.mark.high_mem
def test_transformers_chat():
    with TransformersChatChoicesService(
        ModelPath('meta-llama/Llama-3.2-1B-Instruct'),
        TransformersPipelineKwargs(dict(
            max_new_tokens=20,
            # device=None,
        )),
    ) as llm:
        resp = lang.sync_await(llm.invoke(ChatChoicesRequest([UserMessage('Is water dry?')])))
        print(resp)
        assert resp


# # @pytest.mark.not_docker_guest
# # @pytest.mark.high_mem
# def test_transformers_chat_phi4_tools():
#     with TransformersChatChoicesService(
#         ModelPath('microsoft/Phi-4-mini-instruct'),
#         TransformersPipelineKwargs(dict(
#             max_new_tokens=20,
#             # device=None,
#         )),
#     ) as llm:
#         resp = llm.invoke(ChatChoicesRequest([UserMessage('Is water dry?')]))
#         print(resp)
#         assert resp
