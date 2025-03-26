import contextlib
import typing as ta

from omlish import lang

from ...chat.messages import UserMessage
from ...chat.models import ChatRequest
from ...generative import MaxTokens
from ...generative import Temperature
from ..llamacpp import LlamacppChatModel


if ta.TYPE_CHECKING:
    import llama_cpp

    from .... import llamacpp as lcu

else:
    llama_cpp = lang.proxy_import('llama_cpp')

    lcu = lang.proxy_import('....llamacpp', __package__)


##


def _main() -> None:
    request = ChatRequest.new(
        [UserMessage('Is water dry?')],
        Temperature(.1),
        MaxTokens(64),
    )

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
                for m in request.v
            ],
            max_tokens=1024,
            # stop=['\n'],
        )

        print(output)

        # return ChatResponse(v=[
        #     AiChoice(AiMessage(c['message']['content']))  # noqa
        #     for c in output['choices']  # type: ignore
        # ])


if __name__ == '__main__':
    _main()
