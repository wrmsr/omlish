import typing as ta

from omlish import check

from ....backends.cerebras.clients import REQUIRED_HTTP_HEADERS
from ...chat.choices.services import static_check_is_chat_choices_service
from ...models.configs import ModelName
from ...models.names import ModelNameCollection
from ..openai.compat import OpenaiCompatChatChoicesService
from ..openai.compat import OpenaiCompatChatChoicesServiceBase
from . import names


##


class CerebrasChatChoicesServiceBase(OpenaiCompatChatChoicesServiceBase):
    URL: ta.ClassVar[str] = 'https://api.cerebras.ai/v1/chat/completions'
    API_KEY_ENV: ta.ClassVar[str | None] = 'CEREBRAS_API_KEY'
    EXTRA_HEADERS: ta.ClassVar[ta.Mapping[ta.Any, ta.Any]] = REQUIRED_HTTP_HEADERS

    MODEL_NAMES: ta.ClassVar[ModelNameCollection] = names.MODEL_NAMES
    DEFAULT_MODEL_NAME: ta.ClassVar[ModelName] = ModelName(check.not_none(names.MODEL_NAMES.default))


##


# @omlish-manifest $.minichain.registries.manifests.RegistryManifest(
#     name='cerebras',
#     type='ChatChoicesService',
# )
@static_check_is_chat_choices_service
class CerebrasChatChoicesService(CerebrasChatChoicesServiceBase, OpenaiCompatChatChoicesService):
    pass
