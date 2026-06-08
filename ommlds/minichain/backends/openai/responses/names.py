"""
The Responses backend is selected by explicit name ('openai-responses'); model-name -> backend resolution stays owned
by the canonical openai chat-completions backend, so this manifest deliberately omits `model_names` (it would
otherwise make aliases like 'gpt' ambiguous between the two openai backends). At request time the service still uses
openai's chat model-name table via the inherited `MODEL_NAMES` ClassVar.
"""
from ....specs.manifests import BackendStringsManifest


##


# @omlish-manifest
_RESPONSES_BACKEND_STRINGS_MANIFEST = BackendStringsManifest(
    [
        'ChatChoicesService',
        'ChatChoicesStreamService',
    ],
    'openai-responses',
)
