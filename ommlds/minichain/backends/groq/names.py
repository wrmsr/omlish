r"""
https://console.groq.com/docs/models

curl -X GET "https://api.groq.com/openai/v1/models" -H "Authorization: Bearer $GROQ_API_KEY" -H "Content-Type: application/json" | \
    om j -cp -FR -x 'data[].id' | sort

====

allam-2-7b
canopylabs/orpheus-arabic-saudi
canopylabs/orpheus-v1-english
groq/compound
groq/compound-mini
llama-3.1-8b-instant
llama-3.3-70b-versatile
meta-llama/llama-4-scout-17b-16e-instruct
meta-llama/llama-guard-4-12b
meta-llama/llama-prompt-guard-2-22m
meta-llama/llama-prompt-guard-2-86m
moonshotai/kimi-k2-instruct
moonshotai/kimi-k2-instruct-0905
openai/gpt-oss-120b
openai/gpt-oss-20b
openai/gpt-oss-safeguard-20b
qwen/qwen3-32b
whisper-large-v3
whisper-large-v3-turbo

"""  # noqa
from ...models.names import ModelNameCollection
from ...specs.manifests import BackendStringsManifest


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
