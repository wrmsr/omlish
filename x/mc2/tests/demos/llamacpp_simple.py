import contextlib
import typing as ta  # noqa

from omlish import dataclasses as dc
from omlish import lang
from ommlx.minichain.backends.llamacpp import LlamacppChatModel
from ommlx.minichain.chat.messages import UserMessage

from ...services import Request
from ...services import RequestOption
from ...services import Response
from ...services import ResponseOutput
from ...services import Service_


if ta.TYPE_CHECKING:
    import llama_cpp

    from ommlx import llamacpp as lcu

else:
    llama_cpp = lang.proxy_import('llama_cpp')

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
class LlamacppResponse(Response[LlamacppResponseOutput]):
    output: ta.Any


#


class LlamacppService(Service_[LlamacppRequest, LlamacppResponse], request=LlamacppRequest, response=LlamacppResponse):
    def invoke(self, request: LlamacppRequest) -> LlamacppResponse:
        lcu.install_logging_hook()

        with contextlib.ExitStack() as es:
            llm = es.enter_context(contextlib.closing(llama_cpp.Llama(
                model_path=LlamacppChatModel.model_path,
                verbose=False,
            )))

            output = llm.create_chat_completion(
                messages=[  # noqa
                    dict(  # type: ignore
                        role=LlamacppChatModel.ROLES_MAP[type(m)],
                        content=LlamacppChatModel._get_msg_content(m),  # noqa
                    )
                    for m in [
                        UserMessage(request.message),
                    ]
                ],
                max_tokens=1024,
            )

            return LlamacppResponse(output)


##


def _main() -> None:
    foo_svc = LlamacppService()

    for foo_req in [
        LlamacppRequest('Is water dry?'),
    ]:
        print(foo_req)

        foo_resp = foo_svc.invoke(foo_req)
        print(foo_resp)


if __name__ == '__main__':
    _main()
