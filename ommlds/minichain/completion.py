import typing as ta

from omlish import lang

from .llms.types import LlmOption
from .llms.types import LlmOutput
from .registries.globals import register_type
from .services import Request
from .services import Response
from .services import Service
from .types import Option
from .types import Output


##


class CompletionOption(Option, lang.Abstract, lang.Sealed):
    pass


CompletionOptions: ta.TypeAlias = CompletionOption | LlmOption


##


class CompletionOutput(Output, lang.Abstract, lang.Sealed):
    pass


CompletionOutputs: ta.TypeAlias = CompletionOutput | LlmOutput


##


CompletionRequest: ta.TypeAlias = Request[str, CompletionOptions]

CompletionResponse: ta.TypeAlias = Response[str, CompletionOutputs]

# @omlish-manifest $.minichain.registries.manifests.RegistryTypeManifest
CompletionService: ta.TypeAlias = Service[CompletionRequest, CompletionResponse]

register_type(CompletionService, module=__name__)


def static_check_is_completion_service[T: CompletionService](t: type[T]) -> type[T]:
    return t
