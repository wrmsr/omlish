"""
https://console.groq.com/docs/models

curl -X GET "https://api.groq.com/openai/v1/models" \
     -H "Authorization: Bearer $GROQ_API_KEY" \
     -H "Content-Type: application/json"
"""
from ....models.names import ModelNameCollection
from ...strings.manifests import BackendStringsManifest


##


MODEL_NAMES = ModelNameCollection(
    default='gpt-oss-120b',
    aliases={
        'gpt-oss-120b': 'openai/gpt-oss-120b',
        'openai/gpt-oss-120b': None,

        'gpt-oss-20b': 'openai/gpt-oss-20b',
        'openai/gpt-oss-20b': None,
    },
)


# @omlish-manifest
_BACKEND_STRINGS_MANIFEST = BackendStringsManifest(
    [
        'ChatChoicesService',
        'ChatChoicesStreamService',
    ],
    'groq',
    model_names=MODEL_NAMES,
)
