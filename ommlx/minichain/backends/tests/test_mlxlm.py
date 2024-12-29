import pytest

from omlish import check
from omlish.formats import json
from omlish.secrets.tests.harness import HarnessSecrets
from omlish.testing import pytest as ptu

from ...backends.llamacpp import LlamacppPromptModel
from ...backends.mlxlm import MlxlmChatModel
from ...backends.openai import OpenaiChatModel
from ...chat import Message
from ...chat import SystemMessage
from ...chat import Tool
from ...chat import ToolExecResultMessage
from ...chat import ToolParam
from ...chat import ToolSpec
from ...chat import UserMessage
from ...generative import MaxTokens
from ...generative import Temperature
from ...prompts import PromptRequest


@pytest.mark.not_docker_guest
@ptu.skip.if_cant_import('mlx_lm')
def test_mlxlm():
    llm = MlxlmChatModel('mlx-community/mamba-2.8b-hf-f16')

    resp = llm([UserMessage('Is water dry?')])
    print(resp)
    assert resp.v

    resp = llm('Is water dry?')
    print(resp)
    assert resp.v

