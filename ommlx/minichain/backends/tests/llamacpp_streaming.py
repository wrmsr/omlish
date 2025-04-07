import contextlib
import typing as ta  # noqa

from omlish import check
from omlish import lang

from ...chat.choices import AiChoice
from ...chat.choices import AiChoices
from ...chat.messages import AiMessage
from ...chat.messages import UserMessage
from ...chat.streaming import ChatStreamRequest
from ...chat.streaming import ChatStreamResponse
from ...chat.streaming import ChatStreamService_
from ...resources import Resources
from ..llamacpp import LlamacppChatService


if ta.TYPE_CHECKING:
    import llama_cpp.llama_types

    from ommlx import llamacpp as lcu

else:
    llama_cpp = lang.proxy_import('llama_cpp', extras=['llama_types'])

    lcu = lang.proxy_import('ommlx.llamacpp', __package__)


##


class LlamacppChatStreamService(ChatStreamService_):
    def invoke(self, request: ChatStreamRequest) -> ChatStreamResponse:
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
                    for m in request.chat
                ],
                max_tokens=1024,
                stream=True,
            )

            rs.enter_context(lang.defer(output.close))

            def handle_chunk(chunk: 'llama_cpp.llama_types.ChatCompletionChunk') -> ta.Iterator[AiChoices]:
                check.state(chunk['object'] == 'chat.completion.chunk')
                l: list[AiChoice] = []
                for choice in chunk['choices']:
                    if not (delta := choice.get('delta', {})):
                        continue
                    if not (content := delta.get('content', '')):
                        continue
                    l.append(AiChoice(AiMessage(content)))
                yield l

            return ChatStreamResponse(
                _iterator=lang.flatmap(handle_chunk, output),
                _resources=rs,
            )

        except Exception:
            rs.close()
            raise


##


def _main() -> None:
    foo_svc = LlamacppChatStreamService()

    for foo_req in [
        ChatStreamRequest([UserMessage('Is water dry?')]),
    ]:
        print(foo_req)

        with foo_svc.invoke(foo_req) as foo_resp:
            print(foo_resp)
            for o in foo_resp:
                print(o)


if __name__ == '__main__':
    _main()
