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
        'llama3': 'llama-3.3-70b',

        'gpt-oss-120b': None,
        'gpt-oss': 'gpt-oss-120b',

        'qwen-3-32b': None,
        'qwen3': 'qwen-3-32b',

        ##
        # preview

        'qwen-3-235b-a22b-instruct-2507': None,
        'qwen-3-235b': 'qwen-3-235b-a22b-instruct-2507',

        'zai-glm-4.7': None,
        'glm': 'zai-glm-4.7',
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
