"""
The Responses api uses the same model-name namespace as chat-completions (gpt-4o, gpt-5, ...), so the backend reuses
openai's chat model-name table rather than redeclaring it.
"""
from ....specs.manifests import BackendStringsManifest
from ..names import CHAT_MODEL_NAMES


##


# @omlish-manifest
_RESPONSES_BACKEND_STRINGS_MANIFEST = BackendStringsManifest(
    [
        'ChatChoicesService',
        'ChatChoicesStreamService',
    ],
    'openai-responses',
    model_names=CHAT_MODEL_NAMES,
)
