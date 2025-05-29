import contextlib
import threading
import typing as ta  # noqa

import llama_cpp as lcc

from omlish import check
from omlish import lang

from ....backends import llamacpp as lcu
from ...chat.choices import AiChoice
from ...chat.choices import AiChoices
from ...chat.messages import AiMessage
from ...chat.streaming import ChatStreamRequest
from ...chat.streaming import ChatStreamResponse
from ...chat.streaming import ChatStreamService_
from ...resources import Resources
from .chat import LlamacppChatService
from .format import ROLES_MAP
from .format import get_msg_content


##


# @omlish-manifest ommlds.minichain.backends.manifests.BackendManifest(name='llamacpp', type='ChatStreamService')
class LlamacppChatStreamService(ChatStreamService_, lang.ExitStacked):
    def __init__(self) -> None:
        super().__init__()

        self._lock = threading.Lock()

    @lang.cached_function(transient=True)
    def _load_model(self) -> 'lcc.Llama':
        return self._enter_context(contextlib.closing(lcc.Llama(
            model_path=LlamacppChatService.DEFAULT_MODEL_PATH,
            verbose=False,
        )))

    def invoke(self, request: ChatStreamRequest) -> ChatStreamResponse:
        lcu.install_logging_hook()

        rs = Resources()
        try:
            rs.enter_context(self._lock)

            output = self._load_model().create_chat_completion(
                messages=[  # noqa
                    dict(
                        role=ROLES_MAP[type(m)],
                        content=get_msg_content(m),  # noqa
                    )
                    for m in request.chat
                ],
                max_tokens=1024,
                stream=True,
            )

            def close_output():
                output.close()

            rs.enter_context(lang.defer(close_output))

            def handle_chunk(chunk: 'lcc.llama_types.ChatCompletionChunk') -> ta.Iterator[AiChoices]:
                check.state(chunk['object'] == 'chat.completion.chunk')
                l: list[AiChoice] = []
                for choice in chunk['choices']:
                    # FIXME: check role is assistant
                    # FIXME: stop reason
                    if not (delta := choice.get('delta', {})):
                        continue
                    if not (content := delta.get('content', '')):
                        continue
                    l.append(AiChoice(AiMessage(content)))  # type: ignore
                yield l

            return ChatStreamResponse(
                _iterator=iter(lang.flatmap(handle_chunk, output)),
                _resources=rs,
            )

        except Exception:
            rs.close()
            raise
