from ...chat.choices.services import static_check_is_chat_choices_service
from .compat import OpenaiCompatChatChoicesService


##


# @om-manifest $.minichain.registries.manifests.RegistryManifest(
#     name='openai',
#     type='ChatChoicesService',
# )
@static_check_is_chat_choices_service
class OpenaiChatChoicesService(OpenaiCompatChatChoicesService):
    """The reference instance of the openai-compat chat-completions dialect (see `.compat`)."""
