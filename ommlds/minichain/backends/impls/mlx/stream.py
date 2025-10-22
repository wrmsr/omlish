from omlish import typedvalues as tv

from ....chat.stream.services import ChatChoicesStreamRequest
from ....chat.stream.services import ChatChoicesStreamResponse
from ....chat.stream.services import static_check_is_chat_choices_stream_service
from ....configs import Config
from ....standard import DefaultOptions
from .chat import MlxChatChoicesService


##


# @omlish-manifest $.minichain.backends.strings.manifests.BackendStringsManifest(
#     ['ChatChoicesStreamService'],
#     'mlx',
# )


##


# @omlish-manifest $.minichain.registries.manifests.RegistryManifest(
#     name='mlx',
#     type='ChatChoicesStreamService',
# )
@static_check_is_chat_choices_stream_service
class MlxChatChoicesStreamService:
    def __init__(self, *configs: Config) -> None:
        super().__init__()

        with tv.consume(*configs) as cc:
            self._model = cc.pop(MlxChatChoicesService.DEFAULT_MODEL)
            self._default_options: tv.TypedValues = DefaultOptions.pop(cc)

    READ_CHUNK_SIZE = 64 * 1024

    async def invoke(
            self,
            request: ChatChoicesStreamRequest,
            *,
            max_tokens: int = 4096,  # FIXME: ChatOption
    ) -> ChatChoicesStreamResponse:
        raise NotImplementedError
