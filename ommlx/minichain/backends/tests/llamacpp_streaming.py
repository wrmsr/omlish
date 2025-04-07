import contextlib
import typing as ta  # noqa

from omlish import dataclasses as dc
from omlish import lang

from ...chat.messages import UserMessage
from ...resources import Resources
from ...services import Request
from ...services import RequestOption
from ...services import ResponseOutput
from ...services import Service_
from ...streaming import StreamResponse
from ..llamacpp import LlamacppChatService


if ta.TYPE_CHECKING:
    import llama_cpp.llama_types

    from ommlx import llamacpp as lcu

else:
    llama_cpp = lang.proxy_import('llama_cpp', extras=['llama_types'])

    lcu = lang.proxy_import('ommlx.llamacpp', __package__)


##


class LlamacppRequestOption(RequestOption, lang.Abstract):
    pass


@dc.dataclass(frozen=True)
class LlamacppRequest(Request[LlamacppRequestOption]):
    message: str


#


class LlamacppResponseOutput(ResponseOutput, lang.Abstract):
    pass


@dc.dataclass(frozen=True)
class LlamacppChunk:
    created: int
    choices: ta.Sequence[llama_cpp.llama_types.ChatCompletionStreamResponseChoice]


@dc.dataclass(frozen=True)
class LlamacppResponse(StreamResponse[LlamacppResponseOutput, LlamacppChunk]):
    _iterator: ta.Iterator[LlamacppChunk]

    def __iter__(self) -> ta.Iterator[LlamacppChunk]:
        return self._iterator


#


class LlamacppStreamService(
    Service_[
        LlamacppRequest,
        LlamacppResponse,
    ],
    request=LlamacppRequest,
    response=LlamacppResponse,
):
    def invoke(self, request: LlamacppRequest) -> LlamacppResponse:
        lcu.install_logging_hook()

        rs = Resources()
        try:
            llm = rs.enter_context(contextlib.closing(llama_cpp.Llama(
                model_path=LlamacppChatService.model_path,
                verbose=False,
            )))

            output = llm.create_chat_completion(
                messages=[  # noqa
                    dict(
                        role=LlamacppChatService.ROLES_MAP[type(m)],
                        content=LlamacppChatService._get_msg_content(m),  # noqa
                    )
                    for m in [
                        UserMessage(request.message),
                    ]
                ],
                max_tokens=1024,
                stream=True,
            )

            rs.enter_context(lang.defer(output.close))

            it = (
                LlamacppChunk(
                    o['created'],
                    o['choices'],
                )
                for o in output
            )

            return LlamacppResponse(
                _iterator=it,
                _resources=rs,
            )

        except Exception:
            rs.close()
            raise


##


def _main() -> None:
    foo_svc = LlamacppStreamService()

    for foo_req in [
        LlamacppRequest('Is water dry?'),
    ]:
        print(foo_req)

        with foo_svc.invoke(foo_req) as foo_resp:
            print(foo_resp)
            for o in foo_resp:
                print(o)


if __name__ == '__main__':
    _main()
