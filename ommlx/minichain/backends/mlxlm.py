import typing as ta

from omlish import check
from omlish import lang

from ..chat import AiChoice
from ..chat import AiMessage
from ..chat import ChatModel
from ..chat import ChatRequest
from ..chat import ChatResponse
from ..chat import Message
from ..chat import SystemMessage
from ..chat import UserMessage


if ta.TYPE_CHECKING:
    import mlx_lm
else:
    mlx_lm = lang.proxy_import('mlx_lm')


class MlxlmChatModel(ChatModel):
    DEFAULT_MODEL = (
        # 'mlx-community/DeepSeek-Coder-V2-Lite-Instruct-8bit'
        'mlx-community/Llama-3.3-70B-Instruct-4bit'
        # 'mlx-community/Llama-3.3-70B-Instruct-6bit'
        # 'mlx-community/Llama-3.3-70B-Instruct-8bit'
        # 'mlx-community/Mixtral-8x7B-Instruct-v0.1'
        # 'mlx-community/QwQ-32B-Preview-8bit'
        # 'mlx-community/QwQ-32B-Preview-bf16'
        # 'mlx-community/Qwen2.5-0.5B-4bit'
        # 'mlx-community/Qwen2.5-32B-Instruct-8bit'
        # 'mlx-community/Qwen2.5-Coder-32B-Instruct-8bit'
        # 'mlx-community/mamba-2.8b-hf-f16'
    )

    def __init__(
            self,
            model: str = DEFAULT_MODEL,
    ) -> None:
        super().__init__()
        self._model = model

    ROLES_MAP: ta.ClassVar[ta.Mapping[type[Message], str]] = {
        SystemMessage: 'system',
        UserMessage: 'user',
        AiMessage: 'assistant',
    }

    def _get_msg_content(self, m: Message) -> str | None:
        if isinstance(m, (SystemMessage, AiMessage)):
            return m.s

        elif isinstance(m, UserMessage):
            return check.isinstance(m.c, str)

        else:
            raise TypeError(m)

    def invoke(self, request: ChatRequest) -> ChatResponse:
        model, tokenizer = mlx_lm.load(self._model)

        if not (
                hasattr(tokenizer, 'apply_chat_template') and
                tokenizer.chat_template is not None
        ):
            raise RuntimeError(tokenizer)

        prompt = tokenizer.apply_chat_template(
            [
                dict(
                    role=self.ROLES_MAP[type(m)],
                    content=self._get_msg_content(m),
                )
                for m in request.v
            ],
            tokenize=False,
            add_generation_prompt=True,
        )

        response = mlx_lm.generate(
            model,
            tokenizer,
            prompt=prompt,
            # verbose=True,
        )

        return ChatResponse(v=[
            AiChoice(AiMessage(response))  # noqa
        ])
