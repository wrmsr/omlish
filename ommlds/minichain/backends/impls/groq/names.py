"""
https://console.groq.com/docs/models

curl -X GET "https://api.groq.com/openai/v1/models" \
     -H "Authorization: Bearer $GROQ_API_KEY" \
     -H "Content-Type: application/json"

"compound-beta",
"compound-beta-mini",
"gemma2-9b-it",
"llama-3.1-8b-instant",
"llama-3.3-70b-versatile",
"meta-llama/llama-4-maverick-17b-128e-instruct",
"meta-llama/llama-4-scout-17b-16e-instruct",
"meta-llama/llama-guard-4-12b",
"moonshotai/kimi-k2-instruct",
"openai/gpt-oss-120b",
"openai/gpt-oss-20b",
"qwen/qwen3-32b",
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
