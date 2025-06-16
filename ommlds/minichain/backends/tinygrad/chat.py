# ruff: noqa: PERF402

from omlish import check
from omlish import lang

from ....backends.tinygrad.models import llama3 as tgl3
from ...chat.choices.services import ChatChoicesRequest
from ...chat.choices.services import ChatChoicesResponse
from ...chat.choices.services import static_check_is_chat_choices_service
from ...chat.choices.types import AiChoice
from ...chat.messages import AiMessage
from ...chat.messages import SystemMessage
from ...chat.messages import UserMessage


##


DEFAULT_SIZE: str = '1B'
DEFAULT_TEMPERATURE: float = .85


def _load_model(
        *,
        size: str | None = None,
        temperature: float | None = None,
) -> tgl3.Llama3Llm:
    if size is None:
        size = DEFAULT_SIZE
    if temperature is None:
        temperature = DEFAULT_TEMPERATURE

    from ....backends.tinygrad.models.llama3.fetch import fetch_model
    model = fetch_model(size)

    llm = tgl3.Llama3Llm(
        model,
        size=size,
        temperature=temperature,
    )

    return llm


def _prepare_toks(llm: tgl3.Llama3Llm, request: ChatChoicesRequest) -> list[int]:
    toks = [llm.tokenizer.bos_id]

    for msg in request.v:
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

    return toks


##


# @omlish-manifest $.minichain.registry.RegistryManifest(name='tinygrad_llama3', type='ChatChoicesService')
@static_check_is_chat_choices_service
class TinygradLlama3ChatChoicesService(lang.ExitStacked):
    def __init__(
            self,
            *,
            size: str | None = None,
            temperature: float | None = None,
    ) -> None:
        super().__init__()

        self._size = size
        self._temperature = temperature

    @lang.cached_function(transient=True)
    def _load_model(self) -> tgl3.Llama3Llm:
        check.not_none(self._exit_stack)

        return _load_model(
            size=self._size,
            temperature=self._temperature,
        )

    def invoke(self, request: ChatChoicesRequest) -> ChatChoicesResponse:
        llm = self._load_model()

        toks = _prepare_toks(llm, request)

        out = []
        for s in tgl3.run_llm(llm, toks):
            out.append(s)

        return ChatChoicesResponse([AiChoice(AiMessage(''.join(out)))])
