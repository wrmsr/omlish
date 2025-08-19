import contextlib
import threading
import typing as ta  # noqa

import llama_cpp as lcc

from omlish import check
from omlish import lang
from omlish import typedvalues as tv

from .....backends import llamacpp as lcu
from ....chat.choices.services import ChatChoicesOutputs
from ....chat.stream.services import ChatChoicesStreamRequest
from ....chat.stream.services import ChatChoicesStreamResponse
from ....chat.stream.services import static_check_is_chat_choices_stream_service
from ....chat.stream.types import AiChoiceDelta
from ....chat.stream.types import AiChoiceDeltas
from ....chat.stream.types import AiMessageDelta
from ....configs import Config
from ....models.configs import ModelPath
from ....resources import UseResources
from ....stream.services import new_stream_response
from .chat import LlamacppChatChoicesService
from .format import ROLES_MAP
from .format import get_msg_content


##


# @omlish-manifest $.minichain.registries.manifests.RegistryManifest(
#     name='llamacpp',
#     type='ChatChoicesStreamService',
# )
@static_check_is_chat_choices_stream_service
class LlamacppChatChoicesStreamService(lang.ExitStacked):
    def __init__(self, *configs: Config) -> None:
        super().__init__()

        with tv.consume(*configs) as cc:
            self._model_path = cc.pop(ModelPath(LlamacppChatChoicesService.DEFAULT_MODEL_PATH))

        self._lock = threading.Lock()

    @lang.cached_function(transient=True)
    def _load_model(self) -> 'lcc.Llama':
        return self._enter_context(contextlib.closing(lcc.Llama(
            model_path=self._model_path.v,
            verbose=False,
        )))

    def invoke(self, request: ChatChoicesStreamRequest) -> ChatChoicesStreamResponse:
        lcu.install_logging_hook()

        with UseResources.or_new(request.options) as rs:
            rs.enter_context(self._lock)

            model: ta.Any = self._load_model()  # FIXME: the types are awful lol

            output = model.create_chat_completion(
                messages=[  # noqa
                    dict(
                        role=ROLES_MAP[type(m)],
                        content=get_msg_content(m),  # noqa
                    )
                    for m in request.v
                ],
                max_tokens=1024,
                stream=True,
            )

            def close_output():
                output.close()  # noqa

            rs.enter_context(lang.defer(close_output))

            def yield_choices() -> ta.Generator[AiChoiceDeltas, None, ta.Sequence[ChatChoicesOutputs] | None]:
                for chunk in output:
                    check.state(chunk['object'] == 'chat.completion.chunk')
                    l: list[AiChoiceDelta] = []
                    for choice in chunk['choices']:
                        # FIXME: check role is assistant
                        # FIXME: stop reason
                        if not (delta := choice.get('delta', {})):
                            continue
                        if not (content := delta.get('content', '')):
                            continue
                        l.append(AiChoiceDelta(AiMessageDelta(content)))
                    yield l
                return None

            return new_stream_response(rs, yield_choices())
