"""https://platform.openai.com/docs/api-reference/chat-streaming"""
from ...chat.stream.choices.services import static_check_is_chat_choices_stream_service
from .compat import OpenaiCompatChatChoicesStreamService


##


# @om-manifest $.minichain.registries.manifests.RegistryManifest(
#     name='openai',
#     type='ChatChoicesStreamService',
# )
@static_check_is_chat_choices_stream_service
class OpenaiChatChoicesStreamService(OpenaiCompatChatChoicesStreamService):
    """The reference instance of the openai-compat chat-completions dialect (see `.compat`)."""
