from ...chat.stream.choices.services import static_check_is_chat_choices_stream_service
from ..openai.compat import OpenaiCompatChatChoicesStreamService
from .chat import CerebrasChatChoicesServiceBase


##


# @om-manifest $.minichain.registries.manifests.RegistryManifest(
#     name='cerebras',
#     type='ChatChoicesStreamService',
# )
@static_check_is_chat_choices_stream_service
class CerebrasChatChoicesStreamService(CerebrasChatChoicesServiceBase, OpenaiCompatChatChoicesStreamService):
    pass
