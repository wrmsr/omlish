import typing as ta

from omlish import check
from omlish import lang

from ..chat.messages import AiMessage
from ..chat.messages import Message
from ..chat.messages import SystemMessage
from ..chat.messages import UserMessage
from ..chat.models import AiChoice
from ..chat.models import ChatModel
from ..chat.models import ChatRequest
from ..chat.models import ChatResponse


if ta.TYPE_CHECKING:
    import mlx.nn
    import mlx_lm.utils
else:
    mlx = lang.proxy_import('mlx', extras=['nn'])
    mlx_lm = lang.proxy_import('mlx_lm', extras=['utils'])


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

    class _LoadedModel(ta.NamedTuple):
        model: 'mlx.nn.Module'
        tokenizer: 'mlx_lm.utils.TokenizerWrapper'

    @lang.cached_function(transient=True)
    def _load_model(self) -> _LoadedModel:
        model, tokenizer = mlx_lm.load(self._model)
        return self._LoadedModel(model, tokenizer)

    def invoke(self, request: ChatRequest) -> ChatResponse:
        model, tokenizer = self._load_model()

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
