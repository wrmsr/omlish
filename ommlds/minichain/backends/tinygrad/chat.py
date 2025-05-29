import typing as ta

from omlish import check
from omlish import lang

from ....backends.tinygrad.models import llama3 as tgl3
from ...chat.choices import AiChoice
from ...chat.messages import AiMessage
from ...chat.messages import SystemMessage
from ...chat.messages import UserMessage
from ...chat.services import ChatRequest
from ...chat.services import ChatResponse
from ...chat.services import ChatService


##


# @omlish-manifest ommlds.minichain.backends.manifests.BackendManifest(name='tinygrad_llama3', type='ChatService')
class TinygradLlama3ChatService(ChatService, lang.ExitStacked):
    DEFAULT_SIZE: ta.ClassVar[str] = '1B'
    DEFAULT_TEMPERATURE: ta.ClassVar[float] = .85

    def __init__(
            self,
            *,
            size: str | None = None,
            temperature: float | None = None,
    ) -> None:
        super().__init__()

        self._size = size if size is not None else self.DEFAULT_SIZE
        self._temperature = temperature if temperature is not None else self.DEFAULT_TEMPERATURE

    @lang.cached_function(transient=True)
    def _load_model(self) -> tgl3.Llama3Llm:
        check.not_none(self._exit_stack)

        from ....backends.tinygrad.models.llama3.repl import fetch_model
        model = fetch_model(self._size)

        llm = tgl3.Llama3Llm(
            model,
            size=self._size,
            temperature=self._temperature,
        )

        return llm

    def invoke(self, request: ChatRequest) -> ChatResponse:
        llm = self._load_model()

        #

        toks = [llm.tokenizer.bos_id]

        for msg in request.chat:
            if isinstance(msg, SystemMessage):
                role = 'system'
                msg_s = msg.s
            elif isinstance(msg, UserMessage):
                role = 'user'
                msg_s = check.isinstance(msg.c, str)
            elif isinstance(msg, AiMessage):
                role = 'assistant'
                msg_s = check.not_none(msg.s)
            else:
                raise TypeError(msg)

            toks.extend(llm.encode_message(role, msg_s))

        toks.extend(llm.encode_role('assistant'))

        #

        out = []

        start_pos = llm.prefill(toks[:-1])
        last_tok = toks[-1]
        while True:
            tok = llm.feed(
                [last_tok],
                start_pos,
            )
            tok = tok.item()

            start_pos += 1
            last_tok = tok
            if tok in llm.tokenizer.stop_tokens:
                break

            out.append(llm.tokenizer.decode([tok]))

        #

        return ChatResponse([AiChoice(AiMessage(''.join(out)))])
