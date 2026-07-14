# ruff: noqa: PERF402
import typing as ta

from omcore import check
from omcore import dataclasses as dc
from omcore import lang

from ...chat.choices.services import ChatChoicesOptions
from ...chat.choices.services import ChatChoicesRequest
from ...chat.choices.services import ChatChoicesResponse
from ...chat.choices.services import static_check_is_chat_choices_service
from ...chat.choices.types import ChatChoices
from ...chat.generations import ChatGeneration
from ...chat.messages import AiMessage
from ...chat.messages import Chat
from ...chat.messages import SystemMessage
from ...chat.messages import UserMessage
from ...chat.stream.choices.joining import AiChoicesDeltaJoiner
from ...chat.stream.choices.services import ChatChoicesStreamRequest
from ...chat.stream.choices.services import ChatChoicesStreamResponse
from ...chat.stream.choices.services import static_check_is_chat_choices_stream_service
from ...chat.stream.choices.types import AiChoiceDeltas
from ...chat.stream.choices.types import AiChoicesDeltas
from ...chat.stream.choices.types import ChatChoicesStreamResult
from ...chat.stream.transform.types import AiDeltasTransform
from ...chat.stream.transform.types import AiDeltaTransformAiDeltasTransform
from ...chat.stream.transform.uuids import TypeSequentialMessageUuidAddingAiDeltaTransform
from ...chat.stream.types import ContentAiDelta
from ...chat.types import ChatOption
from ...llms.types import LlmOption
from ...resources import UseResources
from ...services import StreamResponseSink
from ...services import new_stream_response


with lang.auto_proxy_import(globals()):
    from ....backends.tinygrad.models import llama3 as tgl3


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


def _prepare_toks(
        llm: tgl3.Llama3Llm,
        chat: Chat,
        options: ta.Sequence[ChatChoicesOptions],
) -> list[int]:
    toks = [llm.tokenizer.bos_id]

    for msg in chat:
        if isinstance(msg, SystemMessage):
            role = 'system'
            msg_s = check.isinstance(msg.c, str)
        elif isinstance(msg, UserMessage):
            role = 'user'
            msg_s = check.isinstance(msg.c, str)
        elif isinstance(msg, AiMessage):
            role = 'assistant'
            msg_s = check.isinstance(msg.c, str)
        else:
            raise TypeError(msg)

        toks.extend(llm.encode_message(role, msg_s))

    toks.extend(llm.encode_role('assistant'))

    return toks


##


class BaseTinygradLlama3ChatService(lang.ExitStacked, lang.Abstract):
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


##


# @om-manifest $.minichain.registries.manifests.RegistryManifest(
#     name='tinygrad-llama3',
#     type='ChatChoicesService',
# )
@static_check_is_chat_choices_service
class TinygradLlama3ChatChoicesService(BaseTinygradLlama3ChatService):
    async def invoke(self, request: ChatChoicesRequest) -> ChatChoicesResponse:
        llm = self._load_model()
        toks = _prepare_toks(llm, request.v, request.options)

        out = []
        for s in tgl3.run_llm(llm, toks):
            out.append(s)

        return ChatChoicesResponse(ChatChoices([ChatGeneration([AiMessage(''.join(out))])]))


##


# @om-manifest $.minichain.registries.manifests.RegistryManifest(
#     name='tinygrad-llama3',
#     type='ChatChoicesStreamService',
# )
@static_check_is_chat_choices_stream_service
class TinygradLlama3ChatChoicesStreamService(BaseTinygradLlama3ChatService):
    async def invoke(self, request: ChatChoicesStreamRequest) -> ChatChoicesStreamResponse:
        async with UseResources.or_new(request.options) as rs:
            llm = self._load_model()
            toks = _prepare_toks(
                llm,
                request.v,
                request.options.get_any((ChatOption, LlmOption)),  # FIXME  # noqa
            )

            async def inner(sink: StreamResponseSink[AiChoicesDeltas]) -> ChatChoicesStreamResult:
                dts: list[AiDeltasTransform] | None = None
                joiner = AiChoicesDeltaJoiner()

                for s in tgl3.run_llm(llm, toks):
                    csds = AiChoicesDeltas([
                        AiChoiceDeltas([
                            ContentAiDelta(s),
                        ]),
                    ])

                    if dts is None:
                        dts = [
                            # FIXME: YES THIS IS GETTING WORSE TO GET BETTER
                            AiDeltaTransformAiDeltasTransform(
                                TypeSequentialMessageUuidAddingAiDeltaTransform(),
                            )
                            for _ in range(len(csds.choices))
                        ]

                    csds = dc.replace(csds, choices=[
                        dc.replace(cds, deltas=dts[i].transform(cds.deltas))
                        for i, cds in enumerate(csds.choices)
                    ])

                    joiner.add(csds.choices)

                    await sink.emit(csds)

                return ChatChoicesStreamResult(
                    ChatChoices([
                        ChatGeneration(jc)
                        for jc in joiner.build()
                    ]),
                )

            return await new_stream_response(rs, inner)


##


# @om-manifest $.minichain.specs.manifests.BackendStringsManifest(
#     [
#         'ChatChoicesService',
#         'ChatChoicesStreamService',
#     ],
#     'tinygrad-llama3',
# )
