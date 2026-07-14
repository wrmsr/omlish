from ...chat.stream.choices.services import static_check_is_chat_choices_stream_service
from ..openai.compat import OpenaiCompatChatChoicesStreamService
from .chat import GroqChatChoicesServiceBase


##


# @om-manifest $.minichain.registries.manifests.RegistryManifest(
#     name='groq',
#     type='ChatChoicesStreamService',
# )
@static_check_is_chat_choices_stream_service
class GroqChatChoicesStreamService(GroqChatChoicesServiceBase, OpenaiCompatChatChoicesStreamService):
    pass
