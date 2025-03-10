import contextlib
import os.path
import typing as ta

from omlish import check
from omlish import lang

from ..chat.messages import AiMessage
from ..chat.messages import Message
from ..chat.messages import SystemMessage
from ..chat.messages import ToolExecResultMessage
from ..chat.messages import UserMessage
from ..chat.models import AiChoice
from ..chat.models import ChatModel
from ..chat.models import ChatRequest
from ..chat.models import ChatResponse
from ..prompts import PromptModel
from ..prompts import PromptRequest
from ..prompts import PromptResponse


if ta.TYPE_CHECKING:
    import llama_cpp

    from ... import llamacpp as lcu

else:
    llama_cpp = lang.proxy_import('llama_cpp')

    lcu = lang.proxy_import('...llamacpp', __package__)


class LlamacppPromptModel(PromptModel):
    # hf.hf_hub_download(
    #   revision='1ca85c857dce892b673b988ad0aa83f2cb1bbd19',
    #   repo_id='QuantFactory/Meta-Llama-3-8B-GGUF',
    #   filename='Meta-Llama-3-8B.Q8_0.gguf',
    # )
    model_path = os.path.join(
        os.path.expanduser('~/.cache/huggingface/hub'),
        'models--QuantFactory--Meta-Llama-3-8B-GGUF',
        'snapshots',
        '1ca85c857dce892b673b988ad0aa83f2cb1bbd19',
        'Meta-Llama-3-8B.Q8_0.gguf',
    )

    def invoke(self, request: PromptRequest) -> PromptResponse:
        lcu.install_logging_hook()

        llm = llama_cpp.Llama(
            model_path=self.model_path,
        )

        output = llm.create_completion(
            request.v,
            max_tokens=1024,
            stop=['\n'],
        )

        return PromptResponse(v=output['choices'][0]['text'])  # type: ignore


class LlamacppChatModel(ChatModel):
    model_path = os.path.join(
        os.path.expanduser('~/.cache/huggingface/hub'),
        'models--meta-llama--Llama-3.2-3B-Instruct/snapshots/0cb88a4f764b7a12671c53f0838cd831a0843b95/llama-2-7b-chat.Q5_0.gguf',  # noqa
        # 'models--QuantFactory--Meta-Llama-3-8B-GGUF/snapshots/1ca85c857dce892b673b988ad0aa83f2cb1bbd19/Meta-Llama-3-8B.Q8_0.gguf',  # noqa
    )

    ROLES_MAP: ta.ClassVar[ta.Mapping[type[Message], str]] = {
        SystemMessage: 'system',
        UserMessage: 'user',
        AiMessage: 'assistant',
        ToolExecResultMessage: 'tool',
    }

    def _get_msg_content(self, m: Message) -> str | None:
        if isinstance(m, (SystemMessage, AiMessage)):
            return m.s

        elif isinstance(m, UserMessage):
            return check.isinstance(m.c, str)

        else:
            raise TypeError(m)

    def invoke(self, request: ChatRequest) -> ChatResponse:
        lcu.install_logging_hook()

        with contextlib.ExitStack() as es:
            llm = es.enter_context(contextlib.closing(llama_cpp.Llama(
                model_path=self.model_path,
                verbose=False,
            )))

            output = llm.create_chat_completion(
                messages=[  # noqa
                    dict(  # type: ignore
                        role=self.ROLES_MAP[type(m)],
                        content=self._get_msg_content(m),
                    )
                    for m in request.v
                ],
                max_tokens=1024,
                # stop=['\n'],
            )

            return ChatResponse(v=[
                AiChoice(AiMessage(c['message']['content']))  # noqa
                for c in output['choices']  # type: ignore
            ])
