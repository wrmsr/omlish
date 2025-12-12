"""
https://inference-docs.cerebras.ai/models/overview
"""
from ....models.names import ModelNameCollection
from ...strings.manifests import BackendStringsManifest


##


MODEL_NAMES = ModelNameCollection(
    default='gpt-oss-120b',
    aliases={
        'llama3.1-8b': None,
        'llama-3.3-70b': None,
        'gpt-oss-120b': None,
        'qwen-3-32b': None,
    },
)


# @omlish-manifest
_BACKEND_STRINGS_MANIFEST = BackendStringsManifest(
    [
        'ChatChoicesService',
        'ChatChoicesStreamService',
    ],
    'cerebras',
    model_names=MODEL_NAMES,
)
